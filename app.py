from flask import Flask, render_template, jsonify, request
from opcua import Client, ua
import threading
import time

app = Flask(__name__)

OPC_SERVER_URL = "opc.tcp://127.0.0.1:49320"
client = Client(OPC_SERVER_URL)
client.connect()

all_data = {
    "AUTO": client.get_node("ns=2;s=Channel1.Device1.SAA"),
    "STOP": client.get_node("ns=2;s=Channel1.Device1.STOPACTIVATED"),
    "AUTOCOUNT": client.get_node("ns=2;s=Channel1.Device1.AUTOCOUNT"),
    "BADQUALITYCOUNT": client.get_node("ns=2;s=Channel1.Device1.BADQUALITYCOUNT"),
    "CONVEYORFORWARD": client.get_node("ns=2;s=Channel1.Device1.CONVEYORFORWARD"),
    "CONVEYORSTART": client.get_node("ns=2;s=Channel1.Device1.CONVEYORSTART"),
    "CURRENTCYCLE": client.get_node("ns=2;s=Channel1.Device1.CURRENTCYCLETIMECOUNT"),
    "PREVIOUSCYCLE": client.get_node("ns=2;s=Channel1.Device1.PREVIOUSCYCLETIMECOUNT"),
    "QUALITY": client.get_node("ns=2;s=Channel1.Device1.GOOD"),
    "GOODCOUNT": client.get_node("ns=2;s=Channel1.Device1.GOODQUALITYCOUNT"),
    "TOTALQUALITYCOUNT": client.get_node("ns=2;s=Channel1.Device1.TOTALQUALITYCOUNT"),
    "STOPCOUNT": client.get_node("ns=2;s=Channel1.Device1.STOPCOUNT"),
    "TOTALWPKICKED": client.get_node("ns=2;s=Channel1.Device1.TOTALWPKICKED"),
}

def get_all_node_values():
    node_values = {}
    for key, node in all_data.items():
        value = node.get_value()  
        node_values[key] = value
    return node_values

def set_mode(node, state):
    try:
        target_node = all_data.get(node)
        if target_node:
            # Create a DataValue object with the state (only the value, no status or timestamp)
            data_value = ua.DataValue(ua.Variant(state, ua.VariantType.Boolean))
            target_node.set_value(data_value)  # Set the value of the node
            print(f"{node} set to {state}")

    except Exception as e:
        print(f"Error setting mode for {node}: {e}")

@app.route("/homepage")
def home():
    return render_template("homepage.html")

@app.route("/data_hidden")
def dataHidden():
    return render_template("opcdataviewer.html")

@app.route("/data")
def get_data():
    return jsonify(get_all_node_values())


@app.route("/auto_stop")
def autoStopPage():
    return render_template("autostop.html")

@app.route("/current_process")
def currentProcesPage():
    return render_template("currentProcess.html")

@app.route("/oee_results")
def oeeResultsPage():
    return render_template("oeeResultsPage.html")

# Flask route to handle button press
@app.route('/autoStopButton', methods=['POST'])
def button():
    data = request.get_json()
    value = data.get('value')  # Retrieve 'value' from the request body
    if value:  # When value is `true`
        set_mode("AUTO", True)
        set_mode("STOP", False)
    else:  # When value is `false`
        set_mode("AUTO", False)
        set_mode("STOP", True)

    return jsonify({"message": "Nodes updated successfully."})

@app.route("/get_current_process_data")
def get_current_process_data():
    data = get_all_node_values()
    response_data = {
        "TotalWpKicked": data.get("TOTALWPKICKED"),
        "AutoCount": data.get("AUTOCOUNT"),
        "StopCount": data.get("STOPCOUNT"),
        "CurrentMode": "AUTO" if data.get("AUTO") else "STOP",  # Adjust based on your logic
        "BadQualityCount": data.get("BADQUALITYCOUNT"),
        "ConveyorForward": data.get("CONVEYORFORWARD"),
        "ConveyorStart": data.get("CONVEYORSTART"),
        "CurrentCycle": data.get("CURRENTCYCLE"),
        "PreviousCycle": data.get("PREVIOUSCYCLE"),
        "Quality": data.get("QUALITY"),
        "GoodCount": data.get("GOODCOUNT"),
        "TotalQualityCount": data.get("TOTALQUALITYCOUNT"),
        
    }
    return jsonify(response_data)




if __name__ == "__main__":
    # Run the Flask app
    app.run(debug=True)
