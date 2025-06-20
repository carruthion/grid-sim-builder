import pandapower as pp
import pandapower.networks as pn
import pandapower.plotting as plot

def create_ai4dg_lv_network():
    # Katrins grid from AI4DG:
    net = pp.create_empty_network()

    #-------------------busses---------------------------------------------
    #bus l1 --> Bus that L1 runs to
    bus1 = pp.create_bus(net, vn_kv=10., name="HV_Bus")
    bus2 = pp.create_bus(net, vn_kv=0.4, name="Main_Bus")
    bus3 = pp.create_bus(net, vn_kv=0.4, name="Bus3")
    bus4 = pp.create_bus(net, vn_kv=0.4, name="Bus4")
    bus5 = pp.create_bus(net, vn_kv=0.4, name="Bus5")
    bus6 = pp.create_bus(net, vn_kv=0.4, name="Bus6")
    bus7 = pp.create_bus(net, vn_kv=0.4, name="Bus7")
    bus8 = pp.create_bus(net, vn_kv=0.4, name="Bus8")
    bus9 = pp.create_bus(net, vn_kv=0.4, name="Bus9")
    bus10 = pp.create_bus(net, vn_kv=0.4, name="Bus10")
    bus11 = pp.create_bus(net, vn_kv=0.4, name="Bus11")
    bus12 = pp.create_bus(net, vn_kv=0.4, name="Bus12")
    bus13 = pp.create_bus(net, vn_kv=0.4, name="Bus13")
    bus14 = pp.create_bus(net, vn_kv=0.4, name="Bus14")
    bus15 = pp.create_bus(net, vn_kv=0.4, name="Bus15")
    bus16 = pp.create_bus(net, vn_kv=0.4, name="Bus16")
    bus17 = pp.create_bus(net, vn_kv=0.4, name="Bus17")
    bus18 = pp.create_bus(net, vn_kv=0.4, name="Bus18")
    bus19 = pp.create_bus(net, vn_kv=0.4, name="Bus19")
    bus20 = pp.create_bus(net, vn_kv=0.4, name="Bus20")
    bus21 = pp.create_bus(net, vn_kv=0.4, name="Bus21")

    #------------------bus elements----------------------------------------
    pp.create_ext_grid(net, bus=bus1, vm_pu=1.0, va_degree=0., name="Ext_Grid")
    # load1 = pp.create_load(net, bus=bus21, p_mw=0.0272, q_mvar=0., name="households without PV")

    load2 = pp.create_load(net, bus=bus3, p_mw=0.0002, q_mvar=0., name="load_hh_58")
    load3 = pp.create_load(net, bus=bus7, p_mw=0.0002, q_mvar=0., name="load_hh_62")
    load4 = pp.create_load(net, bus=bus7, p_mw=0.0002, q_mvar=0., name="load_hh_64")
    load5 = pp.create_load(net, bus=bus8, p_mw=0.0002, q_mvar=0., name="load_hh_39")
    load6 = pp.create_load(net, bus=bus8, p_mw=0.0002, q_mvar=0., name="load_hh_37")
    load = pp.create_load(net, bus=bus8, p_mw=0.0002, q_mvar=0., name="load_hh_27")
    load8 = pp.create_load(net, bus=bus9, p_mw=0.0002, q_mvar=0., name="load_hh_2")
    load9 = pp.create_load(net, bus=bus9, p_mw=0.0002, q_mvar=0., name="load_hh_8")
    load10 = pp.create_load(net, bus=bus9, p_mw=0.0002, q_mvar=0., name="load_hh_11")
    load11 = pp.create_load(net, bus=bus9, p_mw=0.0002, q_mvar=0., name="load_hh_16")
    load12 = pp.create_load(net, bus=bus13, p_mw=0.0002, q_mvar=0., name="load_hh_13")
    load13 = pp.create_load(net, bus=bus14, p_mw=0.0002, q_mvar=0., name="load_hh_5")
    load14 = pp.create_load(net, bus=bus14, p_mw=0.0002, q_mvar=0., name="load_hh_7")
    load15 = pp.create_load(net, bus=bus16, p_mw=0.0002, q_mvar=0., name="load_hh_26")
    load16 = pp.create_load(net, bus=bus16, p_mw=0.0002, q_mvar=0., name="load_hh_17")
    load17 = pp.create_load(net, bus=bus16, p_mw=0.0002, q_mvar=0., name="load_hh_15")
    load18 = pp.create_load(net, bus=bus18, p_mw=0.0002, q_mvar=0., name="load_hh_9") #Briloner Weg
    load19 = pp.create_load(net, bus=bus5, p_mw=0.0002, q_mvar=0., name="load_hh_51b")
    load20 = pp.create_load(net, bus=bus11, p_mw=0.0002, q_mvar=0., name="load_hh_1a")
    load21 = pp.create_load(net, bus=bus15, p_mw=0.0002, q_mvar=0., name="load_hh_9a") #Warburger Weg
    load22 = pp.create_load(net, bus=bus19, p_mw=0.0002, q_mvar=0., name="load_hh_12")
    load23 = pp.create_load(net, bus=bus19, p_mw=0.0002, q_mvar=0., name="load_hh_16a")
    load24 = pp.create_load(net, bus=bus19, p_mw=0.0002, q_mvar=0., name="load_hh_7a")
    load25 = pp.create_load(net, bus=bus20, p_mw=0.0002, q_mvar=0., name="load_hh_6")
    load26 = pp.create_load(net, bus=bus6, p_mw=0.0002, q_mvar=0., name="load_hh_5a")
    load27 = pp.create_load(net, bus=bus12, p_mw=0.0002, q_mvar=0., name="load_hh_7b")

    #---------------branch elements----------------------------------------
    trafo = pp.create_transformer(net, hv_bus=bus1, lv_bus=bus2, std_type="0.25 MVA 10/0.4 kV", name="Trafo")
    line1 = pp.create_line_from_parameters(net, from_bus=bus2, to_bus=bus3, length_km=0.1006, r_ohm_per_km=0.21, x_ohm_per_km=0.08, c_nf_per_km=0., max_i_ka=0.27, type="cs", name="L1")
    line2 = pp.create_line_from_parameters(net, from_bus=bus3, to_bus=bus7, length_km=0.077, r_ohm_per_km=0.21, x_ohm_per_km=0.08, c_nf_per_km=0., max_i_ka=0.27, type="cs", name="L2")
    line3 = pp.create_line_from_parameters(net, from_bus=bus3, to_bus=bus8, length_km=0.3544, r_ohm_per_km=0.21, x_ohm_per_km=0.08, c_nf_per_km=0., max_i_ka=0.27, type="cs", name="L3")
    line4 = pp.create_line_from_parameters(net, from_bus=bus2, to_bus=bus4, length_km=0.1007, r_ohm_per_km=0.21, x_ohm_per_km=0.08, c_nf_per_km=0., max_i_ka=0.27, type="cs", name="L4")
    line5 = pp.create_line_from_parameters(net, from_bus=bus4, to_bus=bus9, length_km=0.2501, r_ohm_per_km=0.21, x_ohm_per_km=0.08, c_nf_per_km=0., max_i_ka=0.27, type="cs", name="L5")
    line6 = pp.create_line_from_parameters(net, from_bus=bus4, to_bus=bus10, length_km=0.231, r_ohm_per_km=0.21, x_ohm_per_km=0.08, c_nf_per_km=0., max_i_ka=0.27, type="cs", name="L6")
    line7 = pp.create_line_from_parameters(net, from_bus=bus10, to_bus=bus13, length_km=0.0636, r_ohm_per_km=0.21, x_ohm_per_km=0.08, c_nf_per_km=0., max_i_ka=0.27, type="cs", name="L7")
    line8 = pp.create_line_from_parameters(net, from_bus=bus10, to_bus=bus14, length_km=0.0447, r_ohm_per_km=0.21, x_ohm_per_km=0.08, c_nf_per_km=0., max_i_ka=0.27, type="cs", name="L8")
    line9 = pp.create_line_from_parameters(net, from_bus=bus13, to_bus=bus16, length_km=0.0885, r_ohm_per_km=0.21, x_ohm_per_km=0.08, c_nf_per_km=0., max_i_ka=0.27, type="cs", name="L9")
    line10 = pp.create_line_from_parameters(net, from_bus=bus16, to_bus=bus18, length_km=0.1723, r_ohm_per_km=0.21, x_ohm_per_km=0.08, c_nf_per_km=0., max_i_ka=0.27, type="cs", name="L10")
    line11 = pp.create_line_from_parameters(net, from_bus=bus2, to_bus=bus5, length_km=0.2274, r_ohm_per_km=0.21, x_ohm_per_km=0.08, c_nf_per_km=0., max_i_ka=0.27, type="cs", name="L11")
    line12 = pp.create_line_from_parameters(net, from_bus=bus5, to_bus=bus11, length_km=0.0484, r_ohm_per_km=0.21, x_ohm_per_km=0.08, c_nf_per_km=0., max_i_ka=0.27, type="cs", name="L12")
    line13 = pp.create_line_from_parameters(net, from_bus=bus11, to_bus=bus15, length_km=0.0926, r_ohm_per_km=0.21, x_ohm_per_km=0.08, c_nf_per_km=0., max_i_ka=0.27, type="cs", name="L13")
    line14 = pp.create_line_from_parameters(net, from_bus=bus15, to_bus=bus17, length_km=0.0793, r_ohm_per_km=0.21, x_ohm_per_km=0.08, c_nf_per_km=0., max_i_ka=0.27, type="cs", name="L14")
    line15 = pp.create_line_from_parameters(net, from_bus=bus17, to_bus=bus19, length_km=0.094, r_ohm_per_km=0.21, x_ohm_per_km=0.08, c_nf_per_km=0., max_i_ka=0.27, type="cs", name="L15")
    line16 = pp.create_line_from_parameters(net, from_bus=bus17, to_bus=bus20, length_km=0.0262, r_ohm_per_km=0.21, x_ohm_per_km=0.08, c_nf_per_km=0., max_i_ka=0.27, type="cs", name="L16")
    line17 = pp.create_line_from_parameters(net, from_bus=bus2, to_bus=bus6, length_km=0.3292, r_ohm_per_km=0.21, x_ohm_per_km=0.08, c_nf_per_km=0., max_i_ka=0.27, type="cs", name="L17")
    line18 = pp.create_line_from_parameters(net, from_bus=bus6, to_bus=bus12, length_km=0.0318, r_ohm_per_km=0.21, x_ohm_per_km=0.08, c_nf_per_km=0., max_i_ka=0.27, type="cs", name="L18")
    line19 = pp.create_line_from_parameters(net, from_bus=bus2, to_bus=bus21, length_km=0.001, r_ohm_per_km=0.21, x_ohm_per_km=0.08, c_nf_per_km=0., max_i_ka=0.27, type="cs", name="L19")

    #----------------generators---------------------------------------------
    PV_Nr1 = pp.create_sgen(net, bus3, p_mw=0.0083, q_mvar=0.0, name="PV_hh_58")
    PV_Nr2 = pp.create_sgen(net, bus7, p_mw=0.004, q_mvar=0.0, name="PV_hh_62")
    PV_Nr3 = pp.create_sgen(net, bus7, p_mw=0.0068, q_mvar=0.0, name="PV_hh_64")
    PV_Nr4 = pp.create_sgen(net, bus8, p_mw=0.0042, q_mvar=0.0, name="PV_hh_39")
    PV_Nr5 = pp.create_sgen(net, bus8, p_mw=0.0016, q_mvar=0.0, name="PV_hh_37")
    PV_Nr6 = pp.create_sgen(net, bus8, p_mw=0.0115, q_mvar=0.0, name="PV_hh_27")
    PV_Nr7 = pp.create_sgen(net, bus9, p_mw=0.0079, q_mvar=0.0, name="PV_hh_2")
    PV_Nr8 = pp.create_sgen(net, bus9, p_mw=0.0067, q_mvar=0.0, name="PV_hh_8")
    PV_Nr9 = pp.create_sgen(net, bus9, p_mw=0.0091, q_mvar=0.0, name="PV_hh_11")
    PV_Nr10 = pp.create_sgen(net, bus9, p_mw=0.01, q_mvar=0.0, name="PV_hh_16")
    PV_Nr11 = pp.create_sgen(net, bus13, p_mw=0.0127, q_mvar=0.0, name="PV_hh_13")
    PV_Nr12 = pp.create_sgen(net, bus14, p_mw=0.162, q_mvar=0.0, name="PV_hh_5")
    PV_Nr13 = pp.create_sgen(net, bus14, p_mw=0.0108, q_mvar=0.0, name="PV_hh_7")
    PV_Nr14 = pp.create_sgen(net, bus16, p_mw=0.0049, q_mvar=0.0, name="PV_hh_26")
    PV_Nr15 = pp.create_sgen(net, bus16, p_mw=0.009, q_mvar=0.0, name="PV_hh_17")
    PV_Nr16 = pp.create_sgen(net, bus16, p_mw=0.01, q_mvar=0.0, name="PV_hh_15")
    PV_Nr17 = pp.create_sgen(net, bus18, p_mw=0.0084, q_mvar=0.0, name="PV_hh_9") #Briloner Weg
    PV_Nr18 = pp.create_sgen(net, bus5, p_mw=0.0038, q_mvar=0.0, name="PV_hh_51b")
    PV_Nr19 = pp.create_sgen(net, bus11, p_mw=0.0039, q_mvar=0.0, name="PV_hh_1a")
    PV_Nr20 = pp.create_sgen(net, bus15, p_mw=0.0094, q_mvar=0.0, name="PV_hh_9a") #Warburger Weg
    PV_Nr21 = pp.create_sgen(net, bus19, p_mw=0.0099, q_mvar=0.0, name="PV_hh_12")
    PV_Nr22 = pp.create_sgen(net, bus19, p_mw=0.0078, q_mvar=0.0, name="PV_hh_16a")
    PV_Nr23 = pp.create_sgen(net, bus19, p_mw=0.0085, q_mvar=0.0, name="PV_hh_7a")
    PV_Nr24 = pp.create_sgen(net, bus20, p_mw=0.0063, q_mvar=0.0, name="PV_hh_6")
    PV_Nr25 = pp.create_sgen(net, bus6, p_mw=0.006, q_mvar=0.0, name="PV_hh_5a")
    PV_Nr26 = pp.create_sgen(net, bus12, p_mw=0.0099, q_mvar=0.0, name="PV_hh_7b")

    return net
