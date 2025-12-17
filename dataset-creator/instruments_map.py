from pedalboard import load_plugin

instruments_map = {
    0: load_plugin("instruments/instrument0.vst3"),
    1: load_plugin("instruments/instrument1.vst3"),
}

instruments_map[1].load_preset("presets/preset1.vstpreset")
