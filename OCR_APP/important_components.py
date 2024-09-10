# component_selector.py

def get_important_components(code):
    if code == 'library':
        return [
            "ዜግነት",  # Chassis Number
            "ክልል",
            "የሰሌዳ ቁጥር",  # Plate Number
            "የተሽከርካሪው ዓይነት"  # Type of Vehicle
        ]
    elif code == 'CODE2':
        return [
            "አማራጭ 1",  # Option 1
            "አማራጭ 2",  # Option 2
            "አማራጭ 3",  # Option 3
            "አማራጭ 4"  # Option 4
        ]
    else:
        return [
            "አማራጭ 1",  # Option 1
            "አማራጭ 2",  # Option 2
            "አማራጭ 3",  # Option 3
            "አማራጭ 4"  # Option 4
        ]