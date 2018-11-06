__author__ = "Hanmant Lokare"

import pandas as pd
import csv


class generating_kml_file:

    def readTextFile(self, input_file):

        # COMMENT THE BELOW LINES FOR THE SECOND OR MORE TIME YOU RUN THE PROGRAM
        """"
            to convert the text file in csv file
        """""
        input_file_name = input_file + ".txt"
        output_file_name = input_file + ".csv"
        input_file_name_kml = input_file + ".kml"

        """"
            Removing the top 6 unwanted lines
        """
        line_number = open(input_file_name).readlines()
        open(input_file_name, 'w').writelines(line_number[6:])

        """"
            Creating a csv file from text file
        """
        with open(input_file_name, 'r') as infile, open(output_file_name, 'w') as outfile:
            stripped = (line.strip() for line in infile)
            lines = (line.split(",") for line in stripped if line)
            writer = csv.writer(outfile)
            writer.writerows(lines)
        df = pd.read_csv(output_file_name, delimiter='\n', header=None)

        # COMMENT THE ABOVE LINES FOR THE SECOND OR MORE TIME YOU RUN THE PROGRAM

        """"
            Collecting Latitude, Longitude, Both directions,tracking angle, speed and time
            from CSV file 
        """
        latitude = []
        longitude = []
        latitude_direction = []
        longitude_direction = []
        tracking_angle = []
        speed = []
        time = []
        for i in df[0]:
            if i.split(',')[0] == "$GPRMC":
                latitude_direction.append(i.split(',')[4])

                time_element = str(i.split(',')[1])
                hours = float(time_element[:2])
                min = float(time_element[2:4])
                seconds = float(time_element[4:])
                final_time = hours + (min / 60) + (seconds / 3600)
                time.append(final_time)

                tracking_angle.append(i.split(',')[8])

                speed_element = float(i.split(',')[7])
                speed.append(speed_element * 1.151)

                value = i.split(',')[3]
                lat = str(value)
                if len(lat) > 1:
                    degree1 = int(lat[:2])
                    min = float(lat[2:])
                    degree2 = min / 60
                    final_degree = degree1 + degree2
                    latitude.append(final_degree)

                longitude_direction.append(i.split(',')[6])

                value = i.split(',')[5]
                longi = str(value)
                if len(longi) > 1:
                    degree1 = int(longi[:3])
                    min = float(longi[3:])
                    degree2 = min / 60
                    final_degree = degree1 + degree2
                    longitude.append(final_degree)

            else:

                longitude_direction.append(i.split(',')[5])

                time_element = str(i.split(',')[1])
                hours = float(time_element[:2])
                min = float(time_element[2:4])
                seconds = float(time_element[4:])
                final_time = hours + (min / 60) + (seconds / 3600)
                time.append(final_time)

                tracking_angle.append(0.0)

                speed.append(0.0)

                value = i.split(',')[4]
                longi = str(value)
                if len(longi) > 1:
                    degree1 = int(longi[:3])
                    min = float(longi[3:])
                    degree2 = min / 60
                    final_degree = degree1 + degree2
                    longitude.append(final_degree)
                    latitude_direction.append(i.split(',')[3])

                value = i.split(',')[2]
                lat = str(value)
                if len(lat) > 1:
                    degree1 = int(lat[:2])
                    min = float(lat[2:])
                    degree2 = min / 60
                    final_degree = degree1 + degree2
                    latitude.append(final_degree)

        """"
            Calculating cost function to find best route
        """
        total_time = float((float(time[len(time) - 1]) - float(time[0])) * 60)
        max_velocity = float(max(speed))
        print(total_time)
        print(max_velocity)
        Cost = float((total_time / 30)) + 0.5 * float((max_velocity / 60))
        print("Cost for file", input_file, " is ", Cost)

        """"
            Removing all the points which are at parking state
        """
        copy_lat = []
        copy_long = []
        copy_time = []
        copy_speed = []
        copy_tracking_angle = []
        for i in range(len(longitude)):
            # After careful observation i found that speed < 0.115100 is also consider as parking state of the car
            if (speed[i] > 0.011510000000000001):
                copy_lat.append(latitude[i])
                copy_long.append(longitude[i])
                copy_speed.append(speed[i])
                copy_time.append(time[i])
                copy_tracking_angle.append(tracking_angle[i])

        """"
            Removing continous same and redundant data
        """
        copy_lat1 = []
        copy_long1 = []
        copy_time1 = []
        copy_speed1 = []
        copy_tracking_angle1 = []
        boolean_1 = True
        i = 0
        while boolean_1:
            boolean_2 = True
            if i >= (len(copy_time) - 1):
                break
            while boolean_2:
                if i >= (len(copy_time) - 1):
                    break
                if (copy_long[i] == copy_long[i + 1] and copy_lat[i] == copy_lat[i + 1] and copy_speed[i] == copy_speed[
                    i + 1] and copy_time[i] == copy_time[i + 1]):
                    i += 1
                    if i >= (len(copy_time) - 1):
                        break
                    continue
                else:
                    copy_lat1.append(copy_lat[i])
                    copy_long1.append(copy_long[i])
                    copy_speed1.append(copy_speed[i])
                    copy_time1.append(copy_time[i])
                    copy_tracking_angle1.append(copy_tracking_angle[i])
                    i += 1
                    if i >= (len(copy_time) - 1):
                        break
                    break

        """"
            Getting cluster of data where speed <10 and >1
        """
        st_lat = []
        st_long = []
        st_time = []
        st_speed = []
        st_tracking_angle = []
        for i in range(len(copy_lat1)):
            if copy_speed1[i] > 1 and copy_speed1[i] < 10:
                st_lat.append(copy_lat1[i])
                st_long.append(copy_long1[i])
                st_time.append(copy_time1[i])
                st_speed.append(copy_speed1[i])
                st_tracking_angle.append(copy_tracking_angle1[i])

        """"
            Getting all the stops and stop signals
        """
        stops_speed = []
        stops_lat = []
        stops_long = []
        stops_time = []
        stops_tracking_angle = []
        phase = 1

        for i in range(len(st_speed) - 1):
            if st_speed[i] < st_speed[i + 1] and phase == 1:
                pass
            elif st_speed[i] > st_speed[i + 1] and phase == 1:
                phase = 2

            if st_speed[i] > st_speed[i + 1] and phase == 2:
                pass
            elif st_speed[i] < st_speed[i + 1] and phase == 2:
                stops_speed.append(st_speed[i])
                stops_lat.append(st_lat[i])
                stops_long.append(st_long[i])
                stops_time.append(st_time[i])
                stops_tracking_angle.append(st_tracking_angle[i])
                phase = 1

        """"
            Code to neglect almost same stop signs
        """
        stops_speed_copy = []
        stops_lat_copy = []
        stops_long_copy = []
        stops_time_copy = []
        stops_tracking_angle_copy = []
        for i in range(len(stops_speed) - 1):
            if (stops_time[i + 1] - stops_time[i]) > 0.009822222:
                stops_speed_copy.append(stops_speed[i])
                stops_time_copy.append(stops_time[i])
                stops_lat_copy.append(stops_lat[i])
                stops_long_copy.append(stops_long[i])
                stops_tracking_angle_copy.append(stops_tracking_angle[i])
            else:
                i += 1

        """"
            Writing to the kml file
        """
        line = "<?xml version='%s' encoding='%s'?>\n" % ("1.0", "UTF-8")
        line = line + "<kml xmlns='%s'>\n" % ("http://www.opengis.net/kml/2.2")
        line = line + "<Document>\n<Style id='%s'>\n\t<LineStyle>\n\t\t" % "yellowPoly"
        line = line + "<color>Af00ffff</color>\n\t\t<width>6</width>\n\t</LineStyle>\n\t<PolyStyle>\n\t\t"
        line = line + "<color>7f00ff00</color>\n\t</PolyStyle></Style>\n<Placemark><styleUrl>#yellowPoly</styleUrl>\n"
        line = line + "<LineString>\n<Description>Speed in MPH, not altitude.</Description>\n\t<extrude>1</extrude>\n\t"
        line = line + "<tesselate>1</tesselate>\n\t<altitudeMode>absolute</altitudeMode>\n\t<coordinates>\n\t"
        for i in range(len(copy_lat1)):
            line = line + "-%s,%s,%s\n\t" % (str(copy_long1[i]), str(copy_lat1[i]), str(copy_speed1[i]))
        line = line + "</coordinates>\n</LineString>\n</Placemark>\n"
        line = line + "<Style id='redpin'>\n<IconStyle>\n\t<Icon>\n\t\t<href>http://maps.google.com/mapfiles/kml/pushpin/red-pushpin.png</href>\n\t</Icon>\n</IconStyle>\n</Style>"
        for i in range(len(stops_time_copy)):
            line = line + "<Placemark>\n\t <name>Stop</name>\n\t<styleUrl>#redpin</styleUrl>\n\t<description>Stop</description>\n\t"
            line = line + "<Point>\n\t\t<coordinates>-%s,%s</coordinates>\n\t</Point>\n</Placemark>\n" % (
                str(stops_long_copy[i]), str(stops_lat_copy[i]))
        line = line + "</Document>\n</kml>"
        file = open(input_file_name_kml, "w")
        file.write(line)

        return stops_lat_copy, stops_long_copy


def main():
    generate = generating_kml_file()

    temp_lat = []
    temp_long = []
    file_names = ["ZI8G_ERF_2018_08_16_1428", "ZI8H_HJC_2018_08_17_1745", "ZI8J_GKX_2018_08_19_1646",
                  "ZI8K_EV7_2018_08_20_1500", "ZI8N_DG8_2018_08_23_1316", "ZIAA_CTU_2018_10_10_1255",
                  "ZIAB_CIU_2018_10_11_1218", "ZIAC_CO0_2018_10_12_1250"]

    """"
        Calling readTextFile from generate class on each GPS Data file.
    """
    for i in range(8):
        temp_lat1, temp_long1 = generate.readTextFile(file_names[i])
        temp_lat = temp_lat + temp_lat1
        temp_long = temp_long + temp_long1

    # Uncomment every line below this to get only the placemark kml file
    # for i in range(len(temp_long)):
    #     lat_sorted, long_sorted = zip(*sorted(zip(temp_lat, temp_long),key=operator.itemgetter(0), reverse=True))
    #
    #
    # line = "<?xml version='%s' encoding='%s'?>\n" % ("1.0", "UTF-8")
    # line = line + "<kml xmlns='%s'>\n" % ("http://www.opengis.net/kml/2.2")
    # line = line + "<Style id='redpin'>\n<IconStyle>\n\t<Icon>\n\t\t<href>http://maps.google.com/mapfiles/kml/pushpin/red-pushpin.png</href>\n\t</Icon>\n</IconStyle>\n</Style>"
    # for i in range(len(lat_sorted)-1):
    #     if  (long_sorted[i]-long_sorted[i+1]) > 0.0000814:
    #         print("-" + str(long_sorted[i]) + "," + str(lat_sorted[i]))
    #         line = line + "<Placemark>\n\t <name>Stop</name>\n\t<styleUrl>#redpin</styleUrl>\n\t<description>Stop</description>\n\t"
    #         line = line + "<Point>\n\t\t<coordinates>-%s,%s</coordinates>\n\t</Point>\n</Placemark>\n" % (str(long_sorted[i]), str(lat_sorted[i]))
    # line = line + "</Document>\n</kml>"
    # file = open("Placemark.kml", "w")
    # file.write(line)


if __name__ == '__main__':
    main()
