# coding=utf-8

import sys
import json
import transitfeed
from datetime import datetime
from creators.trips_creator import TripsCreator
from core.osm_routes import Route, RouteMaster

WD = "weekday"
SAT = "saturday"
SUN = "sunday"

class TripsCreatorIrtramma(TripsCreator):

    def add_trips_to_schedule(self, schedule, data):

        # Get the routes information
        lines = data.routes

        # line (osm route master | gtfs route)
        for line_id, line in lines.iteritems():

            for itinerary_id, itinerary in line.routes.iteritems():

                # shape for itinerary
                shape_id = _add_shape(schedule, itinerary_id, itinerary)

                #service periods | Horarios
                operations = self._get_itinerary_operation(itinerary)

                #operation | GTFS service periods
                for operation in operations:
                    service_period = self._create_service_period(schedule,
                     operation)

                    horarios = load_times(itinerary, operation)
                    stops = load_stations(itinerary, operation)

                    route = schedule.GetRoute(line_id)

                    add_trips_for_route(schedule, route, itinerary,
                                        service_period, shape_id,
                                        stops, horarios)
        return

    def _get_itinerary_operation(self, itinerary,
                                 filename='data/input_data_irtramma.json'):
        """
            Return a list of str each one with a 'keyword'
            of the service_day or services_days , stops and stop_times
            are include in the file.
        """
        # opening the file
        input_file = open(filename)
        data = json.load(input_file)

        # standard variables
        fr = itinerary.fr.encode('utf-8')
        to = itinerary.to.encode('utf-8')
        start_date = self.config['feed_info']['start_date']
        end_date = self.config['feed_info']['end_date']

        # creating the operation object
        operations = []

        # loop inside operation object
        for operation in data['itinerario'][itinerary.ref]:
            input_fr = operation["from"].encode('utf-8')
            input_to = operation["to"].encode('utf-8')

            # making sure the information from the object match
            if input_fr == fr and input_ == to:

                if operation["operacion"].encode('utf-8') == WD:
                    operation.append(WD)

                if operation["operacion"].encode('utf-8') == SAT:
                    operation.append(SAT)

                if operation["operacion"].enconde('utf-8') == SUN:
                    operation.append(SUN)
        return operations

    def _create_service_period(self, schedule, operation):
        try:
            service = schedule.GetServicePeriod(operation)
            if service is not None:
                return service
        except KeyError:
            print("INFO. No existe el service_period para la operación:",
                  operation, " por lo que será creado")

        if operation == WD:
            service = transitfeed.ServicePeriod(WD)
            service.SetWeekdayService(True)
            service.SetWeekendService(False)
        elif operation == SAT:
            service = transitfeed.ServicePeriod(SAT)
            service.SetWeekdayService(False)
            service.SetWeekendService(False)
            service.SetDayOfWeekHasService(5, True)
        elif operation == SUN:
            service = transitfeed.ServicePeriod(SUN)
            service.SetWeekdayService(False)
            service.SetWeekendService(False)
            service.SetDayOfWeekHasService(6, True)
        else:
            raise KeyError("uknown operation keyword")

        service.SetStartDate(self.config['feed_info']['start_date'])
        service.SetEndDate(self.config['feed_info']['end_date'])
        schedule.AddServicePeriodObject(service)
        return schedule.GetServicePeriod(operation)

def _add_shape(schedule, route_id, osm_r):
    # get shape id
    shape_id = str(route_id)
    try:
        schedule.GetShape(shape_id)
    except KeyError:
        shape = transitfeed.Shape(shape_id)
        for point in osm_r.shape:
            shape.AddPoint(lat=float(point["lat"]), lon=float(point["lon"]))
        schedule.AddShapeObject(shape)

    return shape_id

def add_trips_for_route(schedule, gtfs_route, itinerary, service_period,
                            shape_id, stops, horarios):
    # debug
    # print("DEBUG Adding trips for itinerary", itinerary.name)

    for viaje in horarios:
        indice = 0
        trip = gtfs_route.AddTrip(schedule, headsign=itinerary.name,
                                  service_period=service_period)
        while indice < len(estaciones):
            tiempo = viaje[indice]
            estacion = stops[indice]
            if tiempo != "-":
                tiempo_parada = datetime.strptime(tiempo, "%H:%M")
                tiempo_parada = str(tiempo_parada.time())

                for stop in itinerary.stops:
                    if stop.name == estacion:
                        parada = schedule.GetStop(str(stop.id))
                        trip.AddStopTime(parada, stop_time=str(tiempo_parada))
                        continue

            # add empty attributes to make navitia happy
            trip.block_id = ""
            trip.wheelchair_accessible = ""
            trip.bikes_allowed = ""
            trip.shape_id = shape_id
            trip.direction_id = ""

            indice = indice + 1
    return

def load_stations(route, operation, filename='data/input_data_irtramma.json'):
    input_file = open(filename)
    input_data = json.load(input_file)

    stations = []
    for direction in input_data["itinerario"][route.ref]:
        fr = direction["from"].encode('utf-8')
        to = direction["to"].encode('utf-8')
        data_operation = direction["operacion"].encode('utf-8')
        if (fr == route.fr.encode('utf-8') and
           to == route.to.encode('utf-8') and data_operation == operation):
            for station in direction["estaciones"]:
                stations = stations + [station.encode('utf-8')]

    # debug
        print("(json) estaciones encontradas: " + str(len(stations)))
        for estacion in stations:
            print(estacion)

    return stations

def load_times(route, operation, filename='data/input_data_irtramma.json'):
    input_file = open(filename)
    input_data = json.load(input_file)

    # route_directions = input_data["itinerario"][route.ref]["horarios"]
    times = None
    for direction in input_data["itinerario"][route.ref]:

        fr = direction["from"].encode('utf-8')
        to = direction["to"].encode('utf-8')
        data_operation = direction["operacion"].encode('utf-8')
        if (fr == route.fr.encode('utf-8') and
           to == route.to.encode('utf-8') and data_operation == operation):
            times = direction["horarios"]

    if times is None:
        print("debug: ruta va de", route.fr.encode('utf-8'),
              "hacia", route.to.encode('utf-8'))
        print("error consiguiendo los tiempos de la ruta")

    return times
