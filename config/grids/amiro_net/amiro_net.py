import pandapower as pp
import pandapower.networks as pn
import pandapower.plotting as plot

def create_amiro_lv_network():
    # small Testnet for AMiRo demo
    net = pp.create_empty_network()

    #-------------------busses---------------------------------------------
    bus_hv_bus = pp.create_bus(net, vn_kv=10., name="HV_Bus")       # high voltage bus id 0
    bus_main_bus = pp.create_bus(net, vn_kv=0.4, name="Main_Bus")   # main bus id 1

    bus_ls_1 = pp.create_bus(net, vn_kv=0.4, name="bus_ls_1")       # load  bus id 2
    bus_hh_1 = pp.create_bus(net, vn_kv=0.4, name="bus_hh_1")       # house bus id 3
    bus_hh_2 = pp.create_bus(net, vn_kv=0.4, name="bus_hh_2")       # house bus id 4
    bus_hh_3 = pp.create_bus(net, vn_kv=0.4, name="bus_hh_3")       # house bus id 5
    bus_hh_4 = pp.create_bus(net, vn_kv=0.4, name="bus_hh_4")       # house bus id 6

    #------------------bus elements----------------------------------------
    pp.create_ext_grid(net, bus=bus_hv_bus, vm_pu=1.0, va_degree=0., name="Ext_Grid")

    pp.create_transformer(net, hv_bus=bus_hv_bus, lv_bus=bus_main_bus, std_type="0.25 MVA 10/0.4 kV", name="Trafo")

    # controllable houses
    pp.create_load(net, bus=bus_hh_1, p_mw=0.0002, q_mvar=0, name="load_hh_1")
    pp.create_load(net, bus=bus_hh_2, p_mw=0.0002, q_mvar=0, name="load_hh_2")
    pp.create_load(net, bus=bus_hh_3, p_mw=0.0002, q_mvar=0, name="load_hh_3")
    pp.create_load(net, bus=bus_hh_4, p_mw=0.0002, q_mvar=0, name="load_hh_4")

    # ev loads
    pp.create_load(net, bus=bus_ls_1, p_mw=0.0000, q_mvar=0, name="ev_ls_1")
    pp.create_load(net, bus=bus_hh_1, p_mw=0.0000, q_mvar=0, name="ev_hh_1")
    pp.create_load(net, bus=bus_hh_2, p_mw=0.0000, q_mvar=0, name="ev_hh_2")
    pp.create_load(net, bus=bus_hh_3, p_mw=0.0000, q_mvar=0, name="ev_hh_3")
    pp.create_load(net, bus=bus_hh_4, p_mw=0.0000, q_mvar=0, name="ev_hh_4")

    # non-controllable houses (dummy houses)
    pp.create_load(net, bus=bus_hh_1, p_mw=0.0002, q_mvar=0, name="load_hh_1_01")
    pp.create_load(net, bus=bus_hh_1, p_mw=0.0002, q_mvar=0, name="load_hh_1_02")
    pp.create_load(net, bus=bus_hh_1, p_mw=0.0002, q_mvar=0, name="load_hh_1_03")
    pp.create_load(net, bus=bus_hh_1, p_mw=0.0002, q_mvar=0, name="load_hh_1_04")
    pp.create_load(net, bus=bus_hh_1, p_mw=0.0002, q_mvar=0, name="load_hh_1_05")

    pp.create_load(net, bus=bus_hh_2, p_mw=0.0002, q_mvar=0, name="load_hh_2_01")
    pp.create_load(net, bus=bus_hh_2, p_mw=0.0002, q_mvar=0, name="load_hh_2_02")
    pp.create_load(net, bus=bus_hh_2, p_mw=0.0002, q_mvar=0, name="load_hh_2_03")
    pp.create_load(net, bus=bus_hh_2, p_mw=0.0002, q_mvar=0, name="load_hh_2_04")
    pp.create_load(net, bus=bus_hh_2, p_mw=0.0002, q_mvar=0, name="load_hh_2_05")

    pp.create_load(net, bus=bus_hh_3, p_mw=0.0002, q_mvar=0, name="load_hh_3_01")
    pp.create_load(net, bus=bus_hh_3, p_mw=0.0002, q_mvar=0, name="load_hh_3_02")
    pp.create_load(net, bus=bus_hh_3, p_mw=0.0002, q_mvar=0, name="load_hh_3_03")
    pp.create_load(net, bus=bus_hh_3, p_mw=0.0002, q_mvar=0, name="load_hh_3_04")
    pp.create_load(net, bus=bus_hh_3, p_mw=0.0002, q_mvar=0, name="load_hh_3_05")

    pp.create_load(net, bus=bus_hh_4, p_mw=0.0002, q_mvar=0, name="load_hh_4_01")
    pp.create_load(net, bus=bus_hh_4, p_mw=0.0002, q_mvar=0, name="load_hh_4_02")
    pp.create_load(net, bus=bus_hh_4, p_mw=0.0002, q_mvar=0, name="load_hh_4_03")
    pp.create_load(net, bus=bus_hh_4, p_mw=0.0002, q_mvar=0, name="load_hh_4_04")
    pp.create_load(net, bus=bus_hh_4, p_mw=0.0002, q_mvar=0, name="load_hh_4_05")

    #------------------pv systems------------------------------------------
    pp.create_sgen(net, bus=bus_hh_1, p_mw=0.0002, q_mvar=0, name="pv_hh_1")
    pp.create_sgen(net, bus=bus_hh_2, p_mw=0.0002, q_mvar=0, name="pv_hh_2")
    pp.create_sgen(net, bus=bus_hh_3, p_mw=0.0002, q_mvar=0, name="pv_hh_3")
    pp.create_sgen(net, bus=bus_hh_4, p_mw=0.0002, q_mvar=0, name="pv_hh_4")

    # pv systems for dummy houses
    pp.create_sgen(net, bus=bus_hh_1, p_mw=0.0002, q_mvar=0, name="pv_hh_1_01")
    pp.create_sgen(net, bus=bus_hh_1, p_mw=0.0002, q_mvar=0, name="pv_hh_1_02")
    pp.create_sgen(net, bus=bus_hh_1, p_mw=0.0002, q_mvar=0, name="pv_hh_1_03")
    pp.create_sgen(net, bus=bus_hh_1, p_mw=0.0002, q_mvar=0, name="pv_hh_1_04")
    pp.create_sgen(net, bus=bus_hh_1, p_mw=0.0002, q_mvar=0, name="pv_hh_1_05")

    pp.create_sgen(net, bus=bus_hh_2, p_mw=0.0002, q_mvar=0, name="pv_hh_2_01")
    pp.create_sgen(net, bus=bus_hh_2, p_mw=0.0002, q_mvar=0, name="pv_hh_2_02")
    pp.create_sgen(net, bus=bus_hh_2, p_mw=0.0002, q_mvar=0, name="pv_hh_2_03")
    pp.create_sgen(net, bus=bus_hh_2, p_mw=0.0002, q_mvar=0, name="pv_hh_2_04")
    pp.create_sgen(net, bus=bus_hh_2, p_mw=0.0002, q_mvar=0, name="pv_hh_2_05")

    pp.create_sgen(net, bus=bus_hh_3, p_mw=0.0002, q_mvar=0, name="pv_hh_3_01")
    pp.create_sgen(net, bus=bus_hh_3, p_mw=0.0002, q_mvar=0, name="pv_hh_3_02")
    pp.create_sgen(net, bus=bus_hh_3, p_mw=0.0002, q_mvar=0, name="pv_hh_3_03")
    pp.create_sgen(net, bus=bus_hh_3, p_mw=0.0002, q_mvar=0, name="pv_hh_3_04")
    pp.create_sgen(net, bus=bus_hh_3, p_mw=0.0002, q_mvar=0, name="pv_hh_3_05")

    pp.create_sgen(net, bus=bus_hh_4, p_mw=0.0002, q_mvar=0, name="pv_hh_4_01")
    pp.create_sgen(net, bus=bus_hh_4, p_mw=0.0002, q_mvar=0, name="pv_hh_4_02")
    pp.create_sgen(net, bus=bus_hh_4, p_mw=0.0002, q_mvar=0, name="pv_hh_4_03")
    pp.create_sgen(net, bus=bus_hh_4, p_mw=0.0002, q_mvar=0, name="pv_hh_4_04")
    pp.create_sgen(net, bus=bus_hh_4, p_mw=0.0002, q_mvar=0, name="pv_hh_4_05")

    #------------------lines-----------------------------------------------
    pp.create_line(net, from_bus=bus_main_bus, to_bus=bus_ls_1, length_km=0.1, std_type="NAYY 4x150 SE", name="line_main_ls_1")
    pp.create_line(net, from_bus=bus_main_bus, to_bus=bus_hh_1, length_km=0.2, std_type="NAYY 4x150 SE", name="line_main_hh_1")
    pp.create_line(net, from_bus=bus_main_bus, to_bus=bus_hh_2, length_km=0.8, std_type="NAYY 4x150 SE", name="line_main_hh_2")
    pp.create_line(net, from_bus=bus_hh_2, to_bus=bus_hh_3, length_km=0.3, std_type="NAYY 4x150 SE", name="line_hh_2_hh_3")
    pp.create_line(net, from_bus=bus_hh_2, to_bus=bus_hh_4, length_km=0.6, std_type="NAYY 4x150 SE", name="line_hh_2_hh_4")

    return net

