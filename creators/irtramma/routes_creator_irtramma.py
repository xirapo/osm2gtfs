#coding=utf-8

from creators.routes_creator import RoutesCreator

class RoutesCreatorIrtramma(RoutesCreator):

    def add_routes_to_schedule(self, schedule, data):

        #Get routes data
        lines = data.get_routes()

        for line_ref, line in sorted(lines.iteritems()):
            route = schedule.AddRoute(
                short_name = line.ref.encode('utf-8'),
                long_name = line.name,
                route_type = "Bus",
                route_id = line_ref)

            # AddRoute method add default agency as default
            route.agency_id = schedule.GetDefaultAgency().agency_id

            route.route_desc = "Ruta de transporte publicoq"

            route.route_color = "ff0000"
            route.route_text_color = "ffffff"

            print("Confirmando que esta usando este route")
            print("informacion del route: ", line.name , "agregada")


        return
