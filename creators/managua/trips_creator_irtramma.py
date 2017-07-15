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
                shape_id = add_shape(schedule, itinerary_id, itinerary)

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
            print("service_period doesn't exist for the operation:",
                    operation, " adding now")

        if operation == WD:
            service = transitfeed.ServicePeriod(WD)
            service.SetWeekdayService(True)
            service.SetWeekendService(False)
        elif operation == SAT:
            service = transitfeed.ServicePeriod(SAT)
            service.SetWeekdayService(False)
