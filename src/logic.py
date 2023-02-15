from datetime import datetime, timedelta
from fake_headers import Headers
from json import dumps
from requests import get
from string import Template

BASE_URL = "https://italoinviaggio.italotreno.it"

def query_data(train_id):
    url = "%s/api/RicercaTrenoService?&TrainNumber=%s" % (BASE_URL, train_id)
    header = Headers(headers=False)
    r = get(url, headers=header.generate())

    # debug
    print("Response code: %s" % r.status_code)
    print(dumps(r.json(), indent = 2))

    if r.status_code != 200:
        print("[Error %s]: %s", r.status_code, r.body)
        return {
            "error": r.status_code
        }
    return r.json()

def clean_data(data):
    lastupdate = data["LastUpdate"]
    not_updated_warning = data["TrainSchedule"]["Distruption"]["Warning"]
    train_number = data["TrainSchedule"]["TrainNumber"]

    departure_station = data["TrainSchedule"]["DepartureStationDescription"]
    departure_station_code = data["TrainSchedule"]["DepartureStation"]
    departure_time = data["TrainSchedule"]["DepartureDate"]
    arrival_station = data["TrainSchedule"]["ArrivalStationDescription"]
    arrival_station_code = data["TrainSchedule"]["ArrivalStation"]
    arrival_time = data["TrainSchedule"]["ArrivalDate"]

    delay_amount = data["TrainSchedule"]["Distruption"]["DelayAmount"]

    next_stop_station = data["TrainSchedule"]["Leg"]["ArrivalStationDescription"]
    next_stop_station_code = data["TrainSchedule"]["Leg"]["ArrivalStation"]
    next_stop_toa = data["TrainSchedule"]["Leg"]["ActualArrivalTime"]
    next_stop_tod = (
        datetime.strptime(data["TrainSchedule"]["Leg"]["EstimatedDepartureTime"], '%H:%M') + \
            timedelta(minutes=delay_amount)
    ).strftime('%H:%M') if delay_amount > 0 else data["TrainSchedule"]["Leg"]["EstimatedDepartureTime"]

    next_stop_platform = \
        data["TrainSchedule"]["Leg"]["EstimatedArrivalPlatform"] \
            if "EstimatedArrivalPlatform" in data["TrainSchedule"]["Leg"].keys() \
                and data["TrainSchedule"]["Leg"]["EstimatedArrivalPlatform"] != None \
                    else None

    train_orientation = \
        data["TrainSchedule"]["Leg"]["TrainOrientation"] \
            if "TrainOrientation" in data["TrainSchedule"]["Leg"].keys() \
                and data["TrainSchedule"]["Leg"]["TrainOrientation"] != None \
                    else None

    past_stops = []
    for stop in data["TrainSchedule"]["StazioniFerme"]:
        past_stops.append({
            "stop_id": stop["StationNumber"],
            "stop_station": stop["LocationDescription"],
            "stop_station_code": stop["LocationCode"],
            "stop_toa": stop["ActualArrivalTime"],
            "stop_tod": stop["ActualDepartureTime"]
        })

    future_stops = []
    for stop in data["TrainSchedule"]["StazioniNonFerme"]:

        future_stops = [
            {
                "stop_id": stop["StationNumber"],
                "stop_station": stop["LocationDescription"],
                "stop_station_code": stop["LocationCode"],
                "stop_toa": stop["EstimatedArrivalTime"],
                "stop_tod": None if (
                    stop["LocationDescription"] == arrival_station and stop["LocationCode"] == arrival_station_code
                ) else stop["EstimatedDepartureTime"],
                "stop_delayed_toa": stop["ActualArrivalTime"] if delay_amount > 0 else None,
                "stop_delayed_tod": None if (
                    delay_amount <= 0 or stop["LocationDescription"] == arrival_station and stop["LocationCode"] == arrival_station_code
                ) else stop["ActualDepartureTime"]
            }
            for stop in data["TrainSchedule"]["StazioniNonFerme"]
        ]


    # loading variables into a clean dictionary
    new_data = {
        "lastupdate": lastupdate,
        "not_updated_warning": not_updated_warning,
        "train_number": train_number,
        "departure_station": departure_station,
        "departure_station_code": departure_station_code,
        "departure_time": departure_time,
        "arrival_station": arrival_station,
        "arrival_station_code": arrival_station_code,
        "arrival_time": arrival_time,
        "delay_amount": delay_amount,
        "next_stop_station": next_stop_station,
        "next_stop_station_code": next_stop_station_code,
        "next_stop_toa": next_stop_toa,
        "next_stop_tod": next_stop_tod,
        "next_stop_platform": next_stop_platform,
        "train_orientation": train_orientation,
        "past_stops": past_stops,
        "future_stops": future_stops
    }

    return new_data

def format_message(data):

        # header
        message = "<b>⌛️ Last update: %s</b>\n" % data["lastupdate"]
        if data["not_updated_warning"] == True:
            message += "<b>⚠️ Warning: train data not updated.</b>\n"
            message += "<b>⚠️ Probably ou're shown old data</b>\n\n"
        message += "<b>🚆 Train %s from %s [%s] to %s [%s]</b>\n" % (
            data["train_number"],
            data["departure_station"],
            data["departure_station_code"],
            data["arrival_station"],
            data["arrival_station_code"]
        )

        # delay
        if data["delay_amount"] > 0:
            message += "<b>⚠️ Delay: %s minutes</b>\n" % data["delay_amount"]
        
        # next stop
        # next stop is also last
        if data["next_stop_station"] == data["arrival_station"] and \
            data["next_stop_station_code"] == data["arrival_station_code"]:
            message += "<b>🚉 Next stop: %s [%s] (%s)</b>\n\n" % (
                data["next_stop_station"],
                data["next_stop_station_code"],
                data["next_stop_toa"]
            )
        else:
            message += "<b>🚉 Next stop: %s [%s] (%s - %s)</b>\n" % (
                data["next_stop_station"],
                data["next_stop_station_code"],
                data["next_stop_toa"],
                data["next_stop_tod"]
            )
        
        # additonal info
        if data["next_stop_platform"] != None and data["next_stop_platform"] != "":
            message += "\t- Next stop platform: %s\n" % data["next_stop_platform"]
        if data["train_orientation"] != None and data["train_orientation"] != "":
            message += "\t- Train orientation: %s\n" % data["train_orientation"]

        message += "\n"

        # past stops
        message += "Past stops:\n"
        for stop in data["past_stops"]:
            message += "\t ✔️ %s (%s - %s)\n" % (
                stop["stop_station"],
                stop["stop_toa"],
                stop["stop_tod"]
            )

        message += "\n"

        # future stops
        last_stop_template = Template(
            "\t⏱️ $station_name ($toa)\n"
        )
        delayed_last_stop_template = Template(
            "\t<b> ⏱️ $station_name <s>($toa)</s> ($delayed_toa)</b>\n"
        )
        stop_template = Template(
            "\t ⏱️ $station_name ($toa - $tod)\n"
        )
        delayed_stop_template = Template(
            "\t ⏱️ $station_name <s>($toa - $tod)</s> ($delayed_toa - $delayed_tod)\n"
        )
        
        message += "Future stops:\n"
        for stop in data["future_stops"]:
            
            if stop["stop_station"] == data["arrival_station"] and \
                stop["stop_station_code"] == data["arrival_station_code"]:

                # last stop case + delayed
                if stop["stop_delayed_toa"] != None:
                    message += delayed_last_stop_template.substitute(
                        station_name=stop["stop_station"],
                        toa=stop["stop_toa"],
                        delayed_toa=stop["stop_delayed_toa"]
                    )
                else:
                    # last stop case
                    message += last_stop_template.substitute(
                        station_name=stop["stop_station"],
                        toa=stop["stop_toa"]
                    )
            else:
                # generic stop case + delayed
                if stop["stop_delayed_toa"] != None and \
                    stop["stop_delayed_tod"] != None:
                    message += delayed_stop_template.substitute(
                        station_name=stop["stop_station"],
                        toa=stop["stop_toa"],
                        tod=stop["stop_tod"],
                        delayed_toa=stop["stop_delayed_toa"],
                        delayed_tod=stop["stop_delayed_tod"]
                    )
                else:
                    # generic stop case
                    message += stop_template.substitute(
                        station_name=stop["stop_station"],
                        toa=stop["stop_toa"],
                        tod=stop["stop_tod"]
                    )
        
        # debug
        print(dumps(message, indent = 2))
        return message