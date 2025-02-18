import xml.etree.ElementTree as ET
from copy import deepcopy
import os
from xml.dom import minidom
import math
import numpy as np


def calculate_sweep_offset(half_span, sweep_percent):
    """
    Calculate the x-offset at the tip based on sweep percentage and span.

    Args:
        half_span (float): Half-span of the wing
        sweep_percent (float): Sweep angle in percentage (0-100)

    Returns:
        float: x-offset at the tip
    """
    sweep_angle_rad = math.radians(sweep_percent)
    return half_span * math.tan(sweep_angle_rad)


def calculate_half_span(aspect_ratio, chord=1.0):
    """
    Calculate the half-span based on aspect ratio and chord.

    Args:
        aspect_ratio (float): Wing aspect ratio
        chord (float): Wing chord length (default=1.0)

    Returns:
        float: Half-span of the wing
    """
    # AR = (2*half_span)^2 / (2*half_span*chord)
    # AR = 2*half_span/chord
    # half_span = AR*chord/2
    return (aspect_ratio * chord) / 2


def create_wing_xml(name, aspect_ratio, sweep_percent, foil_name, output_dir="generated_wings"):
    """
    Creates an XFLR5 XML file for a wing with specified parameters.

    Args:
        name (str): Name of the aircraft
        aspect_ratio (float): Wing aspect ratio
        sweep_percent (float): Sweep angle in degrees (0-100)
        foil_name (str): Name of the airfoil to use
        output_dir (str): Directory to save the generated XML files
    """
    # Calculate geometric parameters
    half_span = calculate_half_span(aspect_ratio)
    sweep_offset = calculate_sweep_offset(half_span, sweep_percent)

    # [Rest of the XML structure remains the same until sections...]
    root = ET.Element("xflplane", version="1.0")

    units = ET.SubElement(root, "Units")
    ET.SubElement(units, "length_unit_to_meter").text = "0.3048"
    ET.SubElement(units, "area_unit_to_m2").text = "0.092903"
    ET.SubElement(units, "mass_unit_to_kg").text = "0.453592"
    ET.SubElement(units, "speed_unit_to_ms").text = "0.3048"
    ET.SubElement(units, "inertia_unit_to_kgm2").text = "0.0421401"

    plane = ET.SubElement(root, "Plane")
    ET.SubElement(plane, "Name").text = name

    style = ET.SubElement(plane, "The_Style")
    ET.SubElement(style, "Stipple").text = "SOLID"
    ET.SubElement(style, "PointStyle").text = "NOSYMBOL"
    ET.SubElement(style, "Width").text = "2"

    color = ET.SubElement(style, "Color")
    ET.SubElement(color, "red").text = "160"
    ET.SubElement(color, "green").text = "160"
    ET.SubElement(color, "blue").text = "164"
    ET.SubElement(color, "alpha").text = "255"

    wing = ET.SubElement(plane, "wing")
    ET.SubElement(wing, "Name").text = "Main Wing"
    ET.SubElement(wing, "Type").text = "MAINWING"

    wing_color = ET.SubElement(wing, "Color")
    ET.SubElement(wing_color, "red").text = "146"
    ET.SubElement(wing_color, "green").text = "164"
    ET.SubElement(wing_color, "blue").text = "111"
    ET.SubElement(wing_color, "alpha").text = "255"

    ET.SubElement(wing, "Description").text = ""
    ET.SubElement(wing, "Position").text = "          0,           0,           0"
    ET.SubElement(wing, "Tip_Strips").text = "1"
    ET.SubElement(wing, "Rx_angle").text = "  0.000"
    ET.SubElement(wing, "Ry_angle").text = "  0.000"
    ET.SubElement(wing, "symmetric").text = "true"
    ET.SubElement(wing, "Two_Sided").text = "true"
    ET.SubElement(wing, "Closed_Inner_Side").text = "false"
    ET.SubElement(wing, "AutoInertia").text = "true"

    inertia = ET.SubElement(wing, "Inertia")
    ET.SubElement(inertia, "Mass").text = "    0.00000"
    ET.SubElement(inertia, "CoG").text = "0.66187, 6.3276e-17, 0.01941"
    ET.SubElement(inertia, "CoG_Ixx").text = "          0"
    ET.SubElement(inertia, "CoG_Iyy").text = "          0"
    ET.SubElement(inertia, "CoG_Izz").text = "          0"
    ET.SubElement(inertia, "CoG_Ixz").text = "          0"

    sections = ET.SubElement(wing, "Sections")

    # Root section
    root_section = ET.SubElement(sections, "Section")
    ET.SubElement(root_section, "y_position").text = "  0.000"
    ET.SubElement(root_section, "Chord").text = "  1.000"
    ET.SubElement(root_section, "xOffset").text = "  0.000"
    ET.SubElement(root_section, "Dihedral").text = "  0.000"
    ET.SubElement(root_section, "Twist").text = "  0.000"
    ET.SubElement(root_section, "x_number_of_panels").text = "13"
    ET.SubElement(root_section, "x_panel_distribution").text = "COSINE"
    ET.SubElement(root_section, "y_number_of_panels").text = "19"
    ET.SubElement(root_section, "y_panel_distribution").text = "INV_SINE"
    ET.SubElement(root_section, "Left_Side_FoilName").text = foil_name
    ET.SubElement(root_section, "Right_Side_FoilName").text = foil_name

    # Tip section
    tip_section = ET.SubElement(sections, "Section")
    ET.SubElement(tip_section, "y_position").text = f"  {half_span:.3f}"
    ET.SubElement(tip_section, "Chord").text = "  1.000"
    ET.SubElement(tip_section, "xOffset").text = f"  {sweep_offset:.3f}"
    ET.SubElement(tip_section, "Dihedral").text = "  0.000"
    ET.SubElement(tip_section, "Twist").text = "  0.000"
    ET.SubElement(tip_section, "x_number_of_panels").text = "13"
    ET.SubElement(tip_section, "x_panel_distribution").text = "COSINE"
    ET.SubElement(tip_section, "y_number_of_panels").text = "5"
    ET.SubElement(tip_section, "y_panel_distribution").text = "UNIFORM"
    ET.SubElement(tip_section, "Left_Side_FoilName").text = foil_name
    ET.SubElement(tip_section, "Right_Side_FoilName").text = foil_name

    # [File writing code remains the same...]
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    rough_string = ET.tostring(root, encoding='unicode')
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="    ")

    xml_lines = pretty_xml.split('\n')
    xml_lines.insert(1, '<!DOCTYPE flow5>')
    pretty_xml = '\n'.join(xml_lines)

    pretty_xml = '\n'.join(line for line in pretty_xml.split('\n') if line.strip())

    filename = os.path.join(output_dir, f"{name}.xml")
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)


ARs = np.arange(4, 7, 1)
sweeps = np.arange(0, 16, 15)
foils = ["MH 32  8.7%", "S2046"]

for foil in foils:
    for AR in ARs:
        for sweep in sweeps:
            create_wing_xml(f"{foil} {AR} {sweep}", AR, sweep, foil)