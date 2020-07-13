# Copyright 2019 snkas
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


class InstantWriter:

    def __init__(self, f):
        self.file_handle = f

    def write(self, s):
        self.file_handle.write(s)
        self.file_handle.flush()


class PropertiesConfig:

    def __init__(self, filename):
        """
        Load properties configuration file.

        :param filename: Filename

        :return: Dictionary of properties
        """

        # Open file
        self.properties = {}
        with open(filename, "rt") as properties_file:

            # Go over each stripped line
            for line in properties_file:
                stripped_line = line.strip()

                # Skip empty lines and commented lines
                if len(stripped_line) > 0 and not stripped_line.startswith('#'):

                    # Split into key-value
                    key_value = stripped_line.split('=')
                    if len(key_value) < 2:
                        raise ValueError("Not a key=value pair: %s" % stripped_line)

                    # Store into map
                    key = key_value[0].strip()
                    value = key_value[1].strip()

                    # No empty value without quotes
                    if len(value) == 0:
                        raise ValueError("Empty value at key: %s" % key)

                    # No duplicates
                    if key in self.properties:
                        raise ValueError("Duplicate key: %s" % key)

                    # Strip away quotes
                    if len(value) >= 2 and value[0] == "\"" and value[len(value) - 1] == "\"":
                        value = value[1:(len(value) - 1)]

                    # Save property value
                    self.properties[key] = value

    def get_property_or_fail(self, key):
        if key in self.properties:
            return self.properties[key]
        else:
            raise ValueError("Property " + str(key) + " does not exist")

    def get_property_or_default(self, key, default_value):
        if key in self.properties:
            return self.properties[key]
        else:
            return default_value

    def get_num_properties(self):
        return len(self.properties)


def _check_is_string_or_fail(str_value):
    if not isinstance(str_value, str):
        raise ValueError("Input is not a string: " + str(str_value))


def parse_int(str_value):
    _check_is_string_or_fail(str_value)
    return int(str_value)


def parse_float(str_value):
    _check_is_string_or_fail(str_value)
    return float(str_value)


def parse_positive_int(str_value):
    res = parse_int(str_value)
    if res < 0:
        raise ValueError("Integer value is not positive: " + str(res))
    else:
        return res


def parse_positive_float(str_value):
    res = parse_float(str_value)
    if res < 0:
        raise ValueError("Float value is not positive: " + str(res))
    else:
        return res


def parse_float_between_0_and_1(str_value):
    res = parse_float(str_value)
    if res < 0.0 or res > 1.0:
        raise ValueError("Float value is not in range [0.0, 1.0]: " + str(res))
    else:
        return res


def parse_positive_int_less_than(str_value, less_than_int_value):
    res = parse_positive_int(str_value)
    if res >= less_than_int_value:
        raise ValueError("Integer value %d is greater than or equal to threshold %d" % (res, less_than_int_value))
    else:
        return res


def read_csv_direct_in_columns(csv_filename, line_values_format):
    """
    Directly read in the entire CSV file.

    :param csv_filename:           CSV filename
    :param line_values_format:     Line format as such: "[int,idx_int,pos_int,float,pos_float,string]+",
                                   e.g., "idx_int,pos_int,float,string,int,pos_float"

    :return: Array of data column arrays (e.g., [ array[idx_int], array[pos_int], array[float],
             array[string], array[int], array[pos_float] ]
    """

    # Determine the formats
    formats = []
    for f in line_values_format.split(","):
        if f != "int" and f != "idx_int" and f != "pos_int" and f != "float" and f != "pos_float" and f != "string":
            raise ValueError(
                "Value format must be one of: int, idx_int, pos_int, float, pos_float, string"
                " (separated by comma without whitespace)"
            )
        formats.append(f)

    # Data will be stored in columns
    data_columns = []
    for i in range(len(formats)):
        data_columns.append([])

    # Read in the CSV file line-by-line
    with open(csv_filename, "r") as csv_file:
        i = 0
        for line in csv_file:
            spl = line.split(",")

            # Check split size
            if len(spl) != len(formats):
                raise ValueError(
                    "Error on line %d: line split length does not match format length\nLine: %s\nFormat: %s"
                    % (i, line.strip(), line_values_format)
                )

            # Save into the data columns
            for j in range(len(spl)):
                if formats[j] == "int":
                    data_columns[j].append(parse_int(spl[j]))
                elif formats[j] == "idx_int":
                    int_val = int(spl[j])
                    if int_val != i:
                        raise ValueError("Index integer constraint violated on line %d" % i)
                    data_columns[j].append(int_val)
                elif formats[j] == "pos_int":
                    data_columns[j].append(parse_positive_int(spl[j]))
                elif formats[j] == "float":
                    data_columns[j].append(parse_float(spl[j]))
                elif formats[j] == "pos_float":
                    data_columns[j].append(parse_positive_float(spl[j]))
                else:
                    data_columns[j].append(spl[j].strip())

            i += 1

    return data_columns
