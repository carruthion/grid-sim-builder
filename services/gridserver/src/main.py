import time
import datetime
import pandapower as pp
import pandapower.networks as pn
import pandapower.plotting as plot
import matplotlib.pyplot as plt
import pandapower.plotting.plotly as pplot
from pandapower.plotting.plotly import pf_res_plotly
import pandas as pd
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import WriteOptions, SYNCHRONOUS
import json
import paho.mqtt.client as mqtt
import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).parent / "config"))

plt.ion()  # Turns on interactive mode

from ai4dg_net.ai4dg_net import create_ai4dg_lv_network
from amiro_net.amiro_net import create_amiro_lv_network

# Settings:
#-----------------------------------------------------------

# Run settings
running_modes = ["automatic", "realtime", "demo", "batch"]
selected_mode = "automatic"  # "automatic", "realtime", "demo", "batch"
run_automatic = True
run_realtime = False
run_demo = False

# Export settings:
export_influx = False
export_mqtt = True

# uncontrolled EV charging based on load profiles:
ev_uncontrolled = False

# select grid model:
grid_models = ["CIGRE", "AI4DG", "AMiRo"]
used_model = "AMiRo"

# MQTT Config
mqtt_broker = "mosquitto"
mqtt_port = 1883
mqtt_topic_prefix = "gridserver"
mqtt_topic_subscribe = mqtt_topic_prefix + "/set"

# InfluxDB Config
token = "6kWqvWTEyEmUTlitYoZZO8qSHi3ePzT-cS1VAH7Vv_7I0_D4k7AVKi3us7yd_BL3ZWjCjFLHb8TyEz5VSVL-zA=="
org = "UniBielefeld"
bucket = "gridserver_bucket"
influx_url = "http://influxdb:8086"

# Time settings
if run_realtime:
    start_time = datetime.datetime(2025, 1, 1, 0, 0, 0)
else:
    start_time = datetime.datetime(2024, 1, 1, 0, 0, 0)
global_time = start_time
global_step = 0


#-----------------------------------------------------------

batch_order = {
    "start_time": start_time,
    "end_time": start_time + datetime.timedelta(days=1),
    "export_influx": export_influx,
    "export_mqtt": export_mqtt,
    "ev_uncontrolled": ev_uncontrolled,
    "batch_id": "batch_1"
}




client = InfluxDBClient(
    url=influx_url,
    token=token,
    org=org
)
write_api = client.write_api(
    write_options=WriteOptions(
        batch_size=1000,      # up to 1000 points in a batch
        flush_interval=10000, # flush every 10 second
        jitter_interval=200, # add up to 0.2s of random delay
        retry_interval=10000  # retry failed writes every 10s
    )
)

hh_objects = {}
ev_list = []

client = mqtt.Client()

# got new settings?
new_mqtt_settings = False
new_power_flow_needed = False

# Create the network depending on the selected model
if used_model == "CIGRE":
    net = pn.create_cigre_network_lv()
elif used_model == "AI4DG":
    net = create_ai4dg_lv_network()
    hh_pv_csv_file = "hh_data/ai4dg_hh_list.csv"
    hh_load_data_file_prefix = "hh_data/load_profiles/h"
    
elif used_model == "AMiRo":
    net = create_amiro_lv_network()
    hh_pv_csv_file = "hh_data/amiro_hh_list.csv"
    hh_load_data_file_prefix = "hh_data/load_profiles/h"
else:
    raise ValueError(f"Unknown model: {used_model}")

hh_total_elec_load_file = "/Electricity_Profile_Total.csv"
hh_ev_charge_load_file = "/ElectricVehicle_ChargeProfile.csv"
hh_pv_power_file = "/Electricity_Profile_PVProduction.csv"

# Time functions
def get_global_time():
    return global_time

def get_global_timestamp():
    return global_time.timestamp()

def get_global_step():
    return global_step

def set_global_time(new_time):
    global global_time
    global global_step
    global_time = new_time
    global_step = int((new_time - start_time).total_seconds() / 60)
    print(f"Set global time to {new_time} ({global_step} minutes)")

def set_global_step(new_step):
    global global_step
    global global_time
    global_step = new_step
    global_time = start_time + datetime.timedelta(minutes=new_step)
    print(f"Set global step to {new_step} ({global_time})")

def time_tick():
    global global_time
    global global_step
    global_step = global_step + 15
    global_time = global_time + datetime.timedelta(minutes=15)

# Load household profiles
def initialize_household_profiles(hh_pv_csv_file):
    """
    @brief Initializes household profiles by loading load, PV, and EV profiles for each household.

    This function reads household data from a CSV file, imports load and PV profiles for each household,
    and checks for the availability of EV profiles. If EV data is available, it is added to the household
    profile; otherwise, the household is marked as not having EV data.

    @param hh_pv_csv_file The file path to the CSV file containing household data.

    @return A DataFrame containing household profiles with load, PV, and EV data (if available).

    @details
    - The function iterates through each household in the input CSV file.
    - For each household, it imports the load and PV profiles using the household ID.
    - It attempts to import EV charge profiles. If the EV data is not found, it logs a message and marks
        the household as not having EV data.
    - The profiles are stored in the DataFrame as objects to accommodate complex data structures.
    """
    hh_objects = load_hh_pv_csv_file(hh_pv_csv_file)

    # load every household with its load and pv profile
    for idx, hh_data in hh_objects.iterrows():
        hh_num = hh_data['hh_id']
        hh_data['load_profile'] = import_hh_load_profiles(hh_num)
        hh_data['pv_profile'] = import_hh_pv_profiles(hh_num)
        # check if ev is available
        try:
            hh_data['ev_profile'] = import_hh_ev_charge_profiles(hh_num)
            hh_data['ev'] = True
        except FileNotFoundError:
            print(f"No EV data for household {hh_num}")
            hh_data['ev'] = False
        # write back
        hh_objects['load_profile'] = hh_objects['load_profile'].astype('object')
        hh_objects['pv_profile'] = hh_objects['pv_profile'].astype('object')
        hh_objects['ev_profile'] = hh_objects['ev_profile'].astype('object')
        hh_objects.at[idx, 'load_profile'] = hh_data['load_profile']
        hh_objects.at[idx, 'pv_profile'] = hh_data['pv_profile']
        if hh_data['ev']:
            hh_objects.at[idx, 'ev_profile'] = hh_data['ev_profile']
            hh_objects.at[idx, 'ev'] = True

    return hh_objects

def get_bus_index_from_load(net, load_name):
    # Filter the loads to find the row with the given load name
    load_row = net.load.loc[net.load["name"] == load_name]
    
    # If the load is found, return its corresponding bus index
    if not load_row.empty:
        return load_row["bus"].iloc[0]
    else:
        print(f"Load '{load_name}' not found in the network.")
        return None

def get_hh_loads_from_net(net):
    # return net.load.set_index("name").index.to_series().to_dict()
    return net.load["name"].tolist()
    # hh_loads = {}
    # for idx, load_data in net.load.iterrows():
    #     hh_loads[load_data['name']] = idx
    # return hh_loads

# Get ev names from net
def get_ev_load_list_from_net(net):
    all_loads = get_hh_loads_from_net(net)
    ev_loads = []
    for load_name in all_loads:
        if "ev" in load_name:
            ev_loads.append(load_name)
    return ev_loads

# Set the power consumption of a household
def set_hh_load(net, hh_name, p_mw, q_mvar):
    load_row = net.load.loc[net.load["name"] == hh_name]

    # Check if the load exists and then set the active and reactive power values
    if not load_row.empty:
        idx = load_row.index[0]
        net.load.at[idx, 'p_mw'] = p_mw
        net.load.at[idx, 'q_mvar'] = q_mvar
    else:
        print(f"Load with name '{hh_name}' not found.")

def get_hh_load(net, hh_name):
    load_row = net.load.loc[net.load["name"] == hh_name]

    # Check if the load exists and then extract the active power value
    if not load_row.empty:
        p_mw_value = load_row["p_mw"].iloc[0]
        return p_mw_value
    else:
        print(f"Load with name '{hh_name}' not found.")
        return None

# add ev charging load to hh
def add_ev_load_to_hh(net, hh_name, p_mw, q_mvar):
    load_row = net.load.loc[net.load["name"] == hh_name]

    # Check if the load exists and then add the active and reactive power values
    if not load_row.empty:
        idx = load_row.index[0]
        net.load.at[idx, 'p_mw'] += p_mw
        net.load.at[idx, 'q_mvar'] += q_mvar
    else:
        print(f"Load with name '{hh_name}' not found.")

def get_bus_voltage(net, bus_name):
    idx = net.bus.index[net.bus['name'] == bus_name]
    if idx.size > 0:
        return net.res_bus.at[idx[0], 'vm_pu']
    return None

def get_hh_voltage(net, hh_name):
    # Get the bus index for the specified load
    bus_idx = get_bus_index_from_load(net, hh_name)
    if bus_idx is None:
        return None
    
    # Retrieve and return the voltage at that bus
    return net.res_bus.at[bus_idx, 'vm_pu']

# Set PV Power 
def set_pv_power(net, pv_name, p_mw, q_mvar):
    mask = net.sgen['name'] == pv_name
    if mask.any():
        net.sgen.loc[mask, 'p_mw'] = abs(p_mw) # has to be a positve value!
        net.sgen.loc[mask, 'q_mvar'] = abs(q_mvar)
    else:
        print(f"PV {pv_name} not found in the network.")

def get_pv_power(net, pv_name):
    mask = net.sgen['name'] == pv_name
    if mask.any():
        return net.sgen.loc[mask, 'p_mw'].iloc[0]
    return None

# Set Battery Power
def set_battery_power(net, battery_name, p_mw, q_mvar):
    mask = net.storage['name'] == battery_name
    if mask.any():
        net.storage.loc[mask, 'p_mw'] = p_mw
        net.storage.loc[mask, 'q_mvar'] = q_mvar
    else:
        print(f"Battery {battery_name} not found in the network.")

# Load hh and pv csv file
def load_hh_pv_csv_file(hh_pv_csv_file):
    hh_pv_csv = pd.read_csv(hh_pv_csv_file)
    return hh_pv_csv
   

# calculate pv area from pv power
def calculate_pv_area(pv_power):
    pv_area = int((pv_power / 0.35) * 1.67)
    return pv_area

# import load profiles
def import_hh_load_profiles(hh_num):
    filename = hh_load_data_file_prefix + str(hh_num) + hh_total_elec_load_file
    load_profiles = pd.read_csv(filename)
    # dont use first row
    load_profiles = load_profiles.iloc[1:]
    keys = load_profiles.keys()
    total_load = load_profiles[keys[0]] + load_profiles[keys[1]] + load_profiles[keys[2]] 
    return total_load

def import_hh_pv_profiles(hh_num):
    filename = hh_load_data_file_prefix + str(hh_num) + hh_pv_power_file
    pv_profiles = pd.read_csv(filename)
    # dont use first row
    pv_profiles = pv_profiles.iloc[1:]
    keys = pv_profiles.keys()
    total_pv = pv_profiles[keys[0]] + pv_profiles[keys[1]] + pv_profiles[keys[2]]
    return total_pv

def import_hh_ev_charge_profiles(hh_num):
    filename = hh_load_data_file_prefix + str(hh_num) + hh_ev_charge_load_file
    ev_charge_profiles = pd.read_csv(filename)
    # dont use first row
    ev_charge_profiles = ev_charge_profiles.iloc[1:]
    keys = ev_charge_profiles.keys()
    total_ev_charge = ev_charge_profiles[keys[0]] + ev_charge_profiles[keys[1]] + ev_charge_profiles[keys[2]]
    return total_ev_charge

# Print household with act load and pv data
def print_act_hh_data(hh_name):
    # Get the mapping of household load names to their indices
    hh_loads = get_hh_loads_from_net(net)
    idx = hh_loads.get(hh_name)
    if idx is None:
        print(f"HH Load {hh_name} not found in the network.")
        return

    # Retrieve the load row from net.load using .loc for fast access
    load = net.load.loc[idx]
    bus_idx = load['bus']
    # Retrieve the corresponding bus data from net.bus
    bus = net.bus.loc[bus_idx]
    # Optionally, retrieve the bus voltage using your get_bus_voltage function
    bus_voltage = get_bus_voltage(net, bus['name'])
    
    print(f"Household: {hh_name}, Bus: {bus['name']}, Voltage: {bus_voltage}, "
          f"P: {load['p_mw']}, Q: {load['q_mvar']}")
    
def handle_batch_message(msg):
    global batch_order
    global export_influx
    global export_mqtt
    global ev_uncontrolled
    # Handle batch message
    try:
        batch_order = batch_order | msg
        export_influx = batch_order.get("export_influx", False)
        export_mqtt = batch_order.get("export_mqtt", False)
        ev_uncontrolled = batch_order.get("ev_uncontrolled", False)

    except Exception as e:
        print(f"Error handling batch message: {e}")


def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(mqtt_topic_subscribe + "/#")

# Handle incoming MQTT messages
def on_message(client, userdata, msg):
    global new_mqtt_settings
    global new_power_flow_needed
    global global_time
    global global_step

    print(f"Received message on topic {msg.topic}: {msg.payload}")
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        topic_parts = msg.topic.split("/")
        
        # Handle EV load setting
        if topic_parts[2] == "hh" and topic_parts[4] == "ev":
            hh_name = topic_parts[3]
            p_mw = payload.get("load", 0) / 1e6
            # add_ev_load_to_hh(net, hh_name, p_mw, 0) # Not this, use set_hh_load instead
            set_hh_load(net, hh_name, p_mw, 0)
            new_power_flow_needed = True
        
        # Handle household load setting
        elif topic_parts[2] == "hh" and topic_parts[4] == "load":
            hh_name = topic_parts[3]
            p_mw = payload.get("load", 0) / 1e6
            q_mvar = payload.get("q_mvar", 0)
            set_hh_load(net, hh_name, p_mw, q_mvar)
            new_power_flow_needed = True
        
        # Handle timestamp setting
        elif topic_parts[2] == "timestamp":
            global global_time
            new_ts = payload.get("timestamp")
            if new_ts:
                # check mode
                if selected_mode == "realtime":
                    print("Timestamp update in realtime mode is not allowed.")
                    return
                if selected_mode == "batch":
                    new_batch_oder = {
                        "start_time": new_ts,
                        "end_time": new_ts + 60,
                    }
                    handle_batch_message(new_batch_oder)
                set_global_time(datetime.datetime.fromtimestamp(new_ts))
                # print(f"Timestamp updated to {global_time}")
                new_mqtt_settings = True
        
        # Handle battery power setting
        elif topic_parts[2] == "battery":
            battery_name = topic_parts[2]
            p_mw = payload.get("p_mw", 0)
            q_mvar = payload.get("q_mvar", 0)
            set_battery_power(net, battery_name, p_mw, q_mvar)
            new_power_flow_needed = True
        
        # Tick message
        elif topic_parts[2] == "tick":
            if not run_realtime:
                new_mqtt_settings = True
                if selected_mode == "batch":
                    new_batch_oder = {
                        "start_time": global_time.timestamp(),
                        "end_time": global_time.timestamp() + 15 * 60,
                    }
                    handle_batch_message(new_batch_oder)
                else:
                    time_tick()
                    print(f"Time ticked to {global_time}")
            else:
                print("Tick message received in realtime mode")

        elif topic_parts[2] == "batch":
            handle_batch_message(payload)
            new_mqtt_settings = True
        
        else:
            print(f"Unhandled topic: {msg.topic}")
    
    except json.JSONDecodeError:
        print("Failed to decode JSON payload")
    except Exception as e:
        print(f"Error handling message: {e}")

def pub_hh_load(hh_name, p_w, ts):
    pub_msg = {
        "hh_name": hh_name,
        "load": p_w,
        "timestamp": ts
    }
    pub_msg = json.dumps(pub_msg)
    client.publish(mqtt_topic_prefix + "/hh/" + hh_name + "/load", pub_msg)

def pub_hh_pv(hh_name, p_w, ts):
    pub_msg = {
        "hh_name": hh_name,
        "pv": p_w,
        "timestamp": ts
    }
    pub_msg = json.dumps(pub_msg)
    client.publish(mqtt_topic_prefix + "/hh/" + hh_name + "/pv", pub_msg)

def pub_hh_voltage(hh_name, voltage, ts):
    pub_msg = {
        "hh_name": hh_name,
        "voltage": voltage,
        "timestamp": ts
    }
    pub_msg = json.dumps(pub_msg)
    client.publish(mqtt_topic_prefix + "/hh/" + hh_name + "/voltage", pub_msg)

def pub_trafo_load(trafo_name, loading, ts):
    pub_msg = {
        "trafo_name": trafo_name,
        "loading": loading,
        "timestamp": ts
    }
    pub_msg = json.dumps(pub_msg)
    client.publish(mqtt_topic_prefix + "/trafo/" + trafo_name + "/loading", pub_msg)

def pub_trafo_load_lv(trafo_name, load_kw, ts):
    pub_msg = {
        "trafo_name": trafo_name,
        "load_lv_kw": load_kw,
        "timestamp": ts
    }
    pub_msg = json.dumps(pub_msg)
    client.publish(mqtt_topic_prefix + "/trafo/" + trafo_name + "/load_lv_kw", pub_msg)

def pub_ev_load(hh_name, p_w, ts):
    pub_msg = {
        "hh_name": hh_name,
        "ev": p_w,
        "timestamp": ts
    }
    pub_msg = json.dumps(pub_msg)
    client.publish(mqtt_topic_prefix + "/hh/" + hh_name + "/ev", pub_msg)

def pub_hh_data(hh_name, load_w, pv_w, voltage, ts):
    pub_msg = {
        "hh_name": hh_name,
        "load": load_w,
        "pv": pv_w,
        "voltage": voltage,
        "timestamp": ts
    }
    pub_msg = json.dumps(pub_msg)
    client.publish(mqtt_topic_prefix + "/hh/" + hh_name + "/data", pub_msg)

# Export actual state to MQTT or InfluxDB
def export_state(ts, hh_objects):
    """
    @brief Exports the current simulation state for all households, EV loads, and transformers.
    This function collects and publishes data for each household, electric vehicle (EV) load, and transformer
    in the grid simulation. It aggregates total load and PV generation, and publishes the data to InfluxDB
    and/or MQTT, depending on configuration.
    @param ts Timestamp for the current simulation step.
    @param hh_objects DataFrame containing household objects with at least 'hh_name' and 'pv_name' columns.
    @details
    - For each household, retrieves load, PV power, and voltage, then publishes to InfluxDB and/or MQTT.
    - Aggregates total load and PV generation across all households and EVs.
    - For each EV load, retrieves and publishes load data.
    - Publishes total load and PV to MQTT.
    - For each transformer, retrieves loading and low-voltage side load, then publishes to InfluxDB and/or MQTT.
    @note
    Requires global variables and functions: net, get_hh_load, get_pv_power, get_hh_voltage, ev_list,
    export_influx, export_mqtt, write_api, bucket, org, pub_hh_data, pub_ev_load, pub_hh_load, pub_hh_pv,
    pub_debug_output, pub_trafo_load, Point.
    """
    total_load = 0
    total_pv = 0


    # Publish actual data to influxdb
    for idx, hh_data in hh_objects.iterrows():
        hh_name = hh_data['hh_name']
        hh_load = get_hh_load(net, hh_name) * 1e6
        hh_pv = get_pv_power(net, hh_data['pv_name']) * 1e6
        hh_voltage = get_hh_voltage(net, hh_name) * 400

        # Add load and pv to total
        total_load += hh_load
        total_pv += hh_pv

        p = Point("household").tag("name", hh_name).field("load", hh_load).field("pv", hh_pv).field("voltage", hh_voltage).time(ts)
        
        # InfluxDB
        if export_influx:
            write_api.write(bucket, org, p)
        # MQTT
        if export_mqtt:
            pub_hh_data(hh_name, hh_load, hh_pv, hh_voltage, ts)
    
    # ev_loads data:
    for ev_load in ev_list:
        ev_load_power = get_hh_load(net, ev_load) * 1e6
        # InfluxDB
        if export_influx:
            p = Point("ev_load").tag("name", ev_load).field("load", ev_load_power).time(ts)
            write_api.write(bucket, org, p)
        # MQTT
        if export_mqtt:
            pub_ev_load(ev_load, ev_load_power, ts)
        total_load += ev_load_power

    if export_mqtt:
        pub_hh_load("total", total_load, ts)
        pub_hh_pv("total", total_pv, ts)
        pub_debug_output()
        
    # Publish Transformer data
    for idx, trafo_data in net.trafo.iterrows():
        trafo_name = trafo_data['name']
        trafo_loading = net.res_trafo.at[idx, 'loading_percent']
        trafo_load_kw = net.res_trafo.at[idx, 'p_lv_mw'] * 1e3
        p = Point("transformer").tag("name", trafo_name).field("loading", trafo_loading).field("load_lv_kw", trafo_load_kw).time(ts)
        
        # InfluxDB
        if export_influx:
            write_api.write(bucket, org, p)
        # MQTT
        if export_mqtt:
            pub_trafo_load(trafo_name, trafo_loading, ts)

# Do power flow calculation and export actual state
def do_power_flow():
    pp.runpp(net)
    export_state(get_global_timestamp(), hh_objects)

def build_html_network_plot():
    # Transformers: Merge name and loading_percent from result table.
    trafo_table = ""
    if not net.trafo.empty and not net.res_trafo.empty:
        df_trafo = pd.concat([net.trafo[['name']], (net.res_trafo[['loading_percent']]).round(2)], axis=1)
        trafo_table = df_trafo.to_html(index=False, border=0)

    # Lines: Merge name and loading_percent.
    line_table = ""
    if not net.line.empty and not net.res_line.empty:
        df_line = pd.concat([net.line[['name']], (net.res_line[['loading_percent']]).round(2)], axis=1)
        line_table = df_line.to_html(index=False, border=0)

    # Loads: Convert p_mw to kW and round to 2 decimals.
    load_table = ""
    if not net.load.empty and not net.res_load.empty:
        # Create the load table merging scheduled p_mw and the power flow result
        df_load = net.load[['name', 'p_mw']]
        # Convert from MW to kW and round to two decimals
        df_load['p_kw'] = (df_load['p_mw'] * 1000).round(2)
        
        # Compute totals in kW
        total_p_kw = (net.load['p_mw'].sum() * 1000).round(2)

        df_load.drop(columns=['p_mw'], inplace=True)
        
        totals_load = pd.DataFrame({
            'name': ['Total'],
            'p_kw': [total_p_kw]
        })
        df_load = pd.concat([df_load, totals_load], ignore_index=True)
        load_table = df_load.to_html(index=False, border=0)

    # Static Generators (Sgen): Convert p_mw to kW and round to 2 decimals.
    sgen_table = ""
    if not net.sgen.empty and not net.res_sgen.empty:
        df_sgen = net.sgen[['name', 'p_mw']]
        df_sgen['p_kw'] = (df_sgen['p_mw'] * 1000).round(2)
        
        total_sgen = (net.sgen['p_mw'].sum() * 1000).round(2)
        df_sgen.drop(columns=['p_mw'], inplace=True)
        
        totals_sgen = pd.DataFrame({
            'name': ['Total'],
            'p_kw': [total_sgen]
        })
        df_sgen = pd.concat([df_sgen, totals_sgen], ignore_index=True)
        sgen_table = df_sgen.to_html(index=False, border=0)

    # Create HTML string
    html_template = """
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Pandapower Network Utilization</title>
        <style>
        body {{ 
            font-family: Arial, sans-serif; 
            margin: 20px; 
            background-color: #f0f0f0; 
        }}
        h1, h2 {{ 
            text-align: center; 
            color: #333; 
        }}
        .table-container {{ 
            width: 80%; 
            margin: 0 auto 30px auto; 
        }}
        table {{ 
            width: 100%; 
            border-collapse: collapse; 
        }}
        th, td {{ 
            padding: 10px; 
            border: 1px solid #ccc; 
            text-align: center; 
        }}
        th {{ 
            background-color: #4CAF50; 
            color: white; 
        }}
        tr:nth-child(even) {{ 
            background-color: #f2f2f2; 
        }}
        tr:hover {{ 
            background-color: #ddd; 
        }}
        </style>
    </head>
    <body>
        <h1>Pandapower Network Utilization Overview</h1>
        
        <div class="table-container">
        <h2>Transformers</h2>
        {trafo_table}
        </div>
        
        <div class="table-container">
        <h2>Lines</h2>
        {line_table}
        </div>
        
        <div class="table-container">
        <h2>Loads (in kW)</h2>
        {load_table}
        </div>
        
        <div class="table-container">
        <h2>Static Generators (Sgen) (in kW)</h2>
        {sgen_table}
        </div>
    </body>
    </html>
    """


    # Insert the generated tables into the template
    html_output = html_template.format(
        trafo_table=trafo_table,
        line_table=line_table,
        load_table=load_table,
        sgen_table=sgen_table
    )
    return html_output

# Publish debug output to MQTT
def pub_debug_output():
    html_info_string = build_html_network_plot()   

    # Generate an interactive Plotly figure of the network
    # fig = pf_res_plotly(net)

    # Save the interactive figure as an HTML string
    # html_site = fig.to_html(full_html=True)
    
    # Publish the HTML string to MQTT
    # client.publish(mqtt_topic_prefix + "/debug/network", html_site)
    client.publish(mqtt_topic_prefix + "/debug/info", html_info_string)



#-----------------------------------------------------------

if __name__ == "__main__":

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(mqtt_broker, mqtt_port, 60)
    
    # Load household profiles
    hh_objects = initialize_household_profiles(hh_pv_csv_file)
    ev_list = get_ev_load_list_from_net(net)

      

    # get duration of simulation
    duration = len(hh_objects.iloc[0, hh_objects.columns.get_loc('load_profile')])
    akt_step = 1

    print("Duration of simulation: ", duration)  

    #-----------------------------------------------------------
    # Demo mode
    #-----------------------------------------------------------

    if selected_mode == "demo":
        print("Starting test mode")

        set_global_time(datetime.datetime.fromtimestamp(1754568180))  # Set the global time to a specific value

        # print household names
        # print("Household names:")
        # for idx, hh_data in hh_objects.iterrows():
        #     print(hh_data['hh_name'])

        # print load names in network
        print("Load names in network:")
        hh_loads = get_hh_loads_from_net(net)
        print(hh_loads)
        # for hh_load in hh_loads:
        #     print(hh_load)
        print("")
        print(get_ev_load_list_from_net(net))

        current_step = get_global_step()  # Cache the current step
        # Loop over household loads
        for _, hh_data in hh_objects.iterrows():
            # Update household load
            p_load = hh_data['load_profile'][(current_step % duration)] / 1e6 # % duration to loop over the profile if the simulation is longer than the profile (typ. 1 year)
            set_hh_load(net, hh_data['hh_name'], p_load, 0)

            # Update PV power and ensure positive value
            p_pv = abs(hh_data['pv_profile'][current_step % duration] / 1e6)
            set_pv_power(net, hh_data['pv_name'], p_pv, 0)

            # If EV is enabled and uncontrolled, update EV load
            if hh_data['ev'] and ev_uncontrolled:
                p_ev = hh_data['ev_profile'][current_step % duration] / 1e6
                add_ev_load_to_hh(net, hh_data['hh_name'], p_ev, 0)
                if export_mqtt:
                    pub_ev_load(hh_data['hh_name'], p_ev * 1e6, get_global_timestamp())

        # Run power flow after all updates
        do_power_flow()

        # Generate an interactive Plotly figure of the network
        fig = pf_res_plotly(net)

        # Save the interactive figure as an HTML file
        fig.write_html("pandapower_network.html")

        # Save SVg image
        # fig.write_image("pandapower_network.svg")

        html_string = build_html_network_plot()
        with open("pandapower_network2.html", "w") as f:
            f.write(html_string)

        # print all ev loads
        ev_loads = get_ev_load_list_from_net(net)
        print("EV loads in network:" + str(ev_loads))

        # Force any remaining data to be written before exiting
        write_api.__del__()
        client.loop_stop()
        client.disconnect()
        print("Test mode finished.")
        # Exit the script
        exit()

    #-----------------------------------------------------------
    # Automatic mode from start_step to end_step (no realtime)
    #-----------------------------------------------------------

    if selected_mode == "automatic":
        print("Starting automatic simulation")
        client.loop_start()

        while True:
            try:
                time.sleep(1)  # Wait for 1 second

                # Check if new tick arrived
                if new_mqtt_settings:
                    new_mqtt_settings = False
                    current_step = get_global_step()  # Cache the current step
                    # print(f"Global step: {current_step}")
                    # Loop over household loads
                    for _, hh_data in hh_objects.iterrows():
                        # Update household load
                        p_load = hh_data['load_profile'][(current_step % duration)] / 1e6 # % duration to loop over the profile if the simulation is longer than the profile (typ. 1 year)
                        set_hh_load(net, hh_data['hh_name'], p_load, 0)

                        # Update PV power and ensure positive value
                        p_pv = abs(hh_data['pv_profile'][current_step % duration] / 1e6)
                        set_pv_power(net, hh_data['pv_name'], p_pv, 0)

                        # If EV is enabled and uncontrolled, update EV load
                        if hh_data['ev'] and ev_uncontrolled:
                            p_ev = hh_data['ev_profile'][current_step % duration] / 1e6
                            add_ev_load_to_hh(net, hh_data['hh_name'], p_ev, 0)
                            if export_mqtt:
                                pub_ev_load(hh_data['hh_name'], p_ev * 1e6, get_global_timestamp())

                    # Run power flow after all updates
                    new_power_flow_needed = False
                    do_power_flow()
                elif new_power_flow_needed:
                    new_power_flow_needed = False
                    do_power_flow()

            except KeyboardInterrupt:
                print("Exiting manual realtime mode.")
                client.loop_stop()
                break
    
    #-----------------------------------------------------------
    # Automatic Realtime mode
    #-----------------------------------------------------------
    elif selected_mode == "realtime":
        print("Starting automatic realtime mode.")
        # Set global time to current time
        set_global_time(datetime.datetime.now())
        do_power_flow()
        client.loop_start()

        while True:
            try:
                time.sleep(10)  # Wait for 10 seconds
                now_ts = datetime.datetime.now().timestamp()
                elapsed = now_ts - get_global_timestamp()

                # Check if a time tick is needed
                if elapsed > 60:
                    set_global_time(datetime.datetime.now())
                    current_step = get_global_step()  # Cache the current step
                    # print(f"Global step: {current_step}")
                    # Loop over household loads
                    for _, hh_data in hh_objects.iterrows():
                        # Update household load
                        p_load = hh_data['load_profile'][current_step % duration] / 1e6 # % duration to loop over the profile if the simulation is longer than the profile (typ. 1 year)
                        set_hh_load(net, hh_data['hh_name'], p_load, 0)

                        # Update PV power and ensure positive value
                        p_pv = abs(hh_data['pv_profile'][current_step % duration] / 1e6)
                        set_pv_power(net, hh_data['pv_name'], p_pv, 0)

                        # If EV is enabled and uncontrolled, update EV load
                        if hh_data['ev'] and ev_uncontrolled:
                            p_ev = hh_data['ev_profile'][current_step % duration] / 1e6
                            add_ev_load_to_hh(net, hh_data['hh_name'], p_ev, 0)
                            if export_mqtt:
                                pub_ev_load(hh_data['hh_name'], p_ev * 1e6, get_global_timestamp())

                    # Run power flow after all updates
                    do_power_flow()

            except KeyboardInterrupt:
                print("Exiting manual realtime mode.")
                client.loop_stop()
                break

    #-----------------------------------------------------------
    # All Manual mode
    #-----------------------------------------------------------
    elif selected_mode == "manual":
        print("Starting manual mode.")
        # Manual mode without realtime
        client.loop_start()
        while True:
            try:
                # Wait for a tick message or manual input
                print("Waiting for manual input or tick message...")
                time.sleep(10)  # Wait for 10 seconds
                if new_power_flow_needed:
                    do_power_flow()
                    new_power_flow_needed = False
                if new_mqtt_settings:
                    print("New settings received via MQTT.")
                    export_state(get_global_timestamp(), hh_objects)
                    new_mqtt_settings = False
            except KeyboardInterrupt:
                print("Exiting manual mode.")
                client.loop_stop()
                break
    
    #-----------------------------------------------------------
    # Batch mode
    #-----------------------------------------------------------
    elif selected_mode == "batch":
        print("Starting batch mode.")
        client.loop_start()
        while True:
            try:
                time.sleep(1)  # Wait for 1 seconds
                if new_mqtt_settings:
                    new_mqtt_settings = False
                    print(batch_order)
                    # Set start time
                    new_time = datetime.datetime.fromtimestamp(batch_order['start_time'])
                    set_global_time(new_time)
                    # Set end time
                    end_time = datetime.datetime.fromtimestamp(batch_order['end_time'])
                    # Loop over timerange
                    while get_global_time() < end_time:
                        current_step = get_global_step() 
                        for _, hh_data in hh_objects.iterrows():
                            # Update household load
                            p_load = hh_data['load_profile'][(current_step % duration)] / 1e6 # % duration to loop over the profile if the simulation is longer than the profile (typ. 1 year)
                            set_hh_load(net, hh_data['hh_name'], p_load, 0)

                            # Update PV power and ensure positive value
                            p_pv = abs(hh_data['pv_profile'][current_step % duration] / 1e6)
                            set_pv_power(net, hh_data['pv_name'], p_pv, 0)

                            # If EV is enabled and uncontrolled, update EV load
                            if hh_data['ev'] and ev_uncontrolled:
                                p_ev = hh_data['ev_profile'][current_step % duration] / 1e6
                                add_ev_load_to_hh(net, hh_data['hh_name'], p_ev, 0)
                                if export_mqtt:
                                    pub_ev_load(hh_data['hh_name'], p_ev * 1e6, get_global_timestamp())

                        # Run power flow after all updates
                        do_power_flow()
                        # Increment global time
                        time_tick()
                        # Wait a bit
                        time.sleep(10)  # Wait for 10 seconds
                    # End of batch processing
                    # Publish finish message
                    finish_msg = {
                        "batch_id": batch_order['batch_id'],
                        "status": "finished"
                    }
                    finish_msg = json.dumps(finish_msg)
                    client.publish(mqtt_topic_prefix + "/batch/finish", finish_msg)
                    # print("Batch processing finished.")
                if new_power_flow_needed:
                    new_power_flow_needed = False
                    do_power_flow()
            except KeyboardInterrupt:
                print("Exiting batch mode.")
                client.loop_stop()
                break
    #-----------------------------------------------------------
    # Cleanup
    #-----------------------------------------------------------
    # Disconnect from MQTT broker
    client.loop_stop()
    client.disconnect()     

    # Force any remaining data to be written before exiting
    write_api.__del__()
    client.disconnect()
