from datetime import datetime, timedelta
from fake_headers import Headers
from requests import get

def query_data(train_id):
    url = "https://italoinviaggio.italotreno.it/api/RicercaTrenoService?&TrainNumber=%s" % train_id
    header = Headers(headers=False)
    r = get(url, headers=header.generate())
    print("Response code: %s" % r.status_code)
    print(r.json())
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
    next_stop_toa = data["TrainSchedule"]["Leg"]["EstimatedArrivalTime"]
    next_stop_tod = data["TrainSchedule"]["Leg"]["EstimatedDepartureTime"]

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
        
        if delay_amount > 0:
            delayed_toa = (
                datetime.strptime(stop["EstimatedArrivalTime"], '%H:%M') +
                timedelta(minutes=delay_amount)
            ).strftime('%H:%M')
            delayed_tod = (
                datetime.strptime(stop["EstimatedDepartureTime"], '%H:%M') +
                timedelta(minutes=delay_amount)
            ).strftime('%H:%M')
        else:
            delayed_toa = None
            delayed_tod = None
        future_stops.append({
            "stop_id": stop["StationNumber"],
            "stop_station": stop["LocationDescription"],
            "stop_station_code": stop["LocationCode"],
            "stop_toa": stop["EstimatedArrivalTime"],
            "stop_tod": stop["EstimatedDepartureTime"],
            "stop_delayed_toa": delayed_toa,
            "stop_delayed_tod": delayed_tod
        })

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
        "past_stops": past_stops,
        "future_stops": future_stops
    }

    return new_data

def format_message(data):
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

        if data["delay_amount"] > 0:
            message += "<b>⚠️ Delay: %s minutes</b>\n" % data["delay_amount"]
        
        message += "<b>🚉 Next stop: %s (%s - %s)</b>\n\n" % (
            data["next_stop_station"],
            data["next_stop_toa"],
            data["next_stop_tod"]
        )

        message += "Past stops:\n"
        for stop in data["past_stops"]:
            message += "\t ✔️ %s (%s - %s)\n" % (
                stop["stop_station"],
                stop["stop_toa"],
                stop["stop_tod"]
            )

        message += "\n"
        
        message += "Future stops:\n"
        for stop in data["future_stops"]:
            if stop["stop_delayed_toa"] != None:
                message += "\t ⏱️ %s <s>(%s - %s)</s> (%s - %s)\n" % (
                    stop["stop_station"],
                    stop["stop_toa"],
                    stop["stop_tod"],
                    stop["stop_delayed_toa"],
                    stop["stop_delayed_tod"]
                )
            else:
               message += "\t ⏱️ %s (%s - %s)\n" % (
                    stop["stop_station"],
                    stop["stop_toa"],
                    stop["stop_tod"]
               )

        return message