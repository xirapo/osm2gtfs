# coding=utf-8

from creators.stops_creator import StopsCreator
from core.osm_routes import Route, RouteMaster

class StopsCreatorIrtramma(StopsCreator):

    def add_stops_to_schedule(self, schedule, data):

        #Get stops
        stops = data.get_stops()

        #add all stops to GTFS
        for stop in stops.values():

            # Add stop to GTFS object
            schedule.AddStop(
                lat=float(stop.lat),
                lng=float(stop.lon),
                name=stop.name,
                stop_id=str(stop.id)
            )
        #Debuggin the script
        print("Debug . agregando parada:", stop.name)

        #adding loose stops objects to route objects
        self.add_stops_to_routes(data)

    def add_stops_to_routes(self, data):

        routes = data.routes
        stops = data.stops

        # Recorriendo los routes
        for ref, route in routes.iteritems():
            # Reemplazando el id de las paradas con el Objecto Stop
            self._fill_stops(stops, route)

        data.routes = routes
        return

    def _fill_stops(self, stops,route):
        """ Llenando el objecto route con el objecto stop con los ids
            relacionados
        """
        if isinstance(route, Route):
            i = 0
            for stop in route.stops:
                if stop in stops:
                    # Replace stop id with Stop objects
                    # TODO: Remove here and use references in TripsCreatorFenix
                    route.stops[i] = stops[stop]
                else:
                    raise RuntimeError("Unknown stop: " + str(stop))
                i += 1

        elif isinstance(route, RouteMaster):
            for route_variant_ref, route_variant in route.routes.iteritems():
                self._fill_stops(stops, route_variant)

        else:
            raise RuntimeError("Unknown Route: " + str(route))
