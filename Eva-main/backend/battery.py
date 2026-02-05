import rclpy
from rclpy.node import Node
from sensor_msgs.msg import BatteryState

holy_battery=0
def voltage_return():
    print(holy_battery)
    return holy_battery
class BatteryStateSubscriber(Node):
    def __init__(self):
        super().__init__('battery_state_subscriber')

        self.subscription = self.create_subscription(
            BatteryState,
            '/battery_state',
            self.battery_callback,
            10
        )

    def battery_callback(self, msg: BatteryState):
        global holy_battery
        holy_battery=msg.voltage
        voltage_return()
        self.get_logger().info(
            f"""
Battery State:
  Voltage     : {msg.voltage:.2f} V

"""
       
        )


def main(args=None):
    rclpy.init(args=args)
    node = BatteryStateSubscriber()
    voltage_return()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
   



if __name__ == '__main__':    
    main()
    voltage_return()