from creators.routes_creator import RoutesCreator

class RoutesCreatorIrtramma():

    def add_routes_to_schedule(self, schedule, data):

        #Get routes data
        lines = data.get_routes()

        for line_ref, line in sorted(lines.iteritems()):
            route = schedule.AddRoute(
                short_name = line.ref.encode('utf-8'),
                long_name = line.name
                route_type = "Bus"
                route_id = line_ref)

            route.route_color = "ff0000"
            route.route_text_color = "ffffff"

            print("informacion del route: ", line.name , "agregada")


        return
