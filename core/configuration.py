# coding=utf-8

import os
import sys
import json
import datetime
import logging
from calendar import monthrange


class Configuration(object):
    """The Configuration class validates and prepares configuration data from
    the config file for further use in the script.

    """

    def __init__(self, args):
        """Contructor function

        This function gets called when Configuration object are created.

        Based on the configuration from the config file it validates and
        prepares all mandatory configuration elements.

        """
        # Load config file from argument of standard location
        self.config = self._load_config(args)

        # Define name for output file
        self.output = self._define_output_file(args)

        # Validate and prepare start and end date
        self._prepare_dates()

    def _load_config(self, args):
        """Loads the configuration. Either the standard location
        (config.json) or a location specified as an command argument.

        :return config: A dictionary of configuration data.

        """
        # Load config json file
        if args.config is not None:
            config = Configuration._load_config_file(args.config)
        elif os.path.isfile('config.json'):
            with open("config.json") as json_file:
                config = Configuration._load_config_file(json_file)
        else:
            sys.stderr.write("Error: No config.json file found.\n")
            sys.exit(0)

        return config

    @staticmethod
    def _load_config_file(configfile):
        """
        Loads json from config file

        :return config: A dictionary of configuration data.

        """
        try:
            config = json.load(configfile)
        except ValueError, e:
            sys.stderr.write('Error: Config json file is invalid.\n')
            print(e)
            sys.exit(0)

        return config

    def _define_output_file(self, args):
        """
        Defines the filename for GTFS file to write.
        Either from config file or command argument.

        :return output: Filename for saving GTFS output file.

        """
        # Get and check filename for gtfs output
        if args.output is not None:
            output_file = args.output
        elif 'output_file' in self.config:
            output_file = self.config['output_file']
        else:
            sys.stderr.write('Error: No filename for gtfs file specified.\n')
            sys.exit(0)

        return output_file

    def _prepare_dates(self):
        """
        Validate and prepare start and end date.
        Either from config file or based on current date.

        """
        config = self.config

        start_date = False
        if 'start_date' in config['feed_info']:
            try:
                start_date = datetime.datetime.strptime(
                    config['feed_info']['start_date'], "%Y%m%d")
            except ValueError, e:
                sys.stderr.write(
                    'Warning: "start_date" from config file %s\n' % str(e))
                pass

        if not start_date:
            # Use first of current month if no start date was specified
            now = datetime.datetime.now()
            start_date = datetime.datetime(day=1, month=now.month,
                                           year=now.year)
            config['feed_info']['start_date'] = str(start_date.year) + \
                str(start_date.month) + "01"
            print("Using the generated start date: " +
                  config['feed_info']['start_date'])

        end_date = False
        if 'end_date' in config['feed_info']:
            try:
                end_date = datetime.datetime.strptime(
                    config['feed_info']['end_date'], "%Y%m%d")
                print("Using the end date from config file: " +
                      config['feed_info']['end_date'])
            except ValueError, e:
                sys.stderr.write(
                    'Warning: "end_date" from config file %s\n' % str(e))
                pass

        if not end_date:

            # Define end date automatically one year from start date
            if start_date.month == 1:
                # Special case in January of each year
                end_date_month = 12
                end_date_year = start_date.year
            else:
                # Regular case for all other months
                end_date_year = start_date.year + 1
                end_date_month = start_date.month - 1

            end_date_day = monthrange(end_date_year, end_date_month)[1]
            end_date = datetime.datetime(day=end_date_day,
                                         month=end_date_month,
                                         year=end_date_year)
            config['feed_info']['end_date'] = str(
                end_date.year) + str(end_date.month) + str(end_date.day)
            print("Using the generated end date: " +
                  config['feed_info']['end_date'])

        # Validate dates
        if start_date > end_date:
            sys.stderr.write('Error: End dates finishes before start date.\n')
            sys.exit(0)
        elif end_date - start_date > datetime.timedelta(days=364):
            sys.stderr.write(
                "Warning: Date range is more than one year.\n")
