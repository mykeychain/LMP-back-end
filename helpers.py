import xml.etree.ElementTree as ET

LMP_BASE_URL = "http://oasis.caiso.com/oasisapi/SingleZip?queryname=PRC_LMP&version=1&"
TYPE_ALIASES = {
                "LMP_PRC": "LMP",
                "LMP_CONG_PRC": "Congestion",
                "LMP_ENE_PRC": "Energy",
                "LMP_LOSS_PRC": "Loss",
                "LMP_GHG_PRC": "Greenhouse Gas"
                }

def url_constructor(start_date, end_date, market_id, node): 
    """ Constructs url for CAISO API request. """

    startdatetime = f'startdatetime={start_date}T07:00-0000'
    enddatetime = f'enddatetime={end_date}T07:00-0000'
    market_run_id = f'market_run_id={market_id}'
    q_node = f'node={node}'

    additional_queries = "&".join([startdatetime, enddatetime, market_run_id, q_node])

    return LMP_BASE_URL + additional_queries


def extract_and_parse(file, fileName): 
    """ Extracts and parses file. Returns dictionary with data. """

    with file.open(fileName) as my_file:
        tree = ET.parse(my_file)
        root = tree.getroot()
        uri = get_xmlns(root.tag)

        report = {}

        # parses and collects metadata into dict entry 'header'
        report['header'] = {}
        header = report['header']
        for metadata in root.iter(f'{uri}REPORT_HEADER'):
            header['MKT_TYPE'] = metadata.find(f'{uri}MKT_TYPE').text
            header['UOM'] = metadata.find(f'{uri}UOM').text

        # parses and collects report data into dict entry 'data'
        report['data'] = {}
        data = report['data']
        for entry in root.iter(f'{uri}REPORT_DATA'): 
            data_item = entry.find(f'{uri}DATA_ITEM').text
            # should name conversion be in front-end?
            converted_name = TYPE_ALIASES[data_item]

            if (converted_name not in data):
                data[converted_name] = []
            
            report_data = {}
            report_data["interval"] = entry.find(f'{uri}INTERVAL_NUM').text
            report_data["value"] = entry.find(f'{uri}VALUE').text
            data[converted_name].append(report_data)
            
    return report


def get_xmlns(tag): 
    """ Gets and returns xmlns from tag as string. """

    tuple = tag.partition("}")
    uri = tuple[0] + "}"
    return uri


def sort_func(response): 
    """ Sorts data by interval. """

    for category in response: 
        response[category].sort(key=sort_criteria)

    return response


def sort_criteria(e):
    """ Defines sorting criteria. """

    return int(e['interval'])


def format_date(date): 
    """ Removes '-' in date to make compatible for url. """

    return "".join(date.split("-"))