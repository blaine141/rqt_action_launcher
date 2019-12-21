import os
import rospy
import rospkg
import roslib
import actionlib

from qt_gui.plugin import Plugin
from python_qt_binding import loadUi
from python_qt_binding.QtWidgets import QWidget, QTreeWidgetItem
from python_qt_binding.QtCore import Qt, QTimer, Signal, Slot

class ActionLauncher(Plugin):

    def __init__(self, context):
        super(ActionLauncher, self).__init__(context)
        # Give QObjects reasonable names
        self.setObjectName('Action Launcher')

        # Create QWidget
        self._widget = QWidget()
        # Get path to UI file which should be in the "resource" folder of this package
        ui_file = os.path.join(rospkg.RosPack().get_path('rqt_action_launcher'), 'resource', 'ActionLauncher.ui')
        # Extend the widget with all attributes and children from UI file
        loadUi(ui_file, self._widget)
        # Give QObjects reasonable names
        self._widget.setObjectName('ActionLauncherUi')
        # Show _widget.windowTitle on left-top of each plugin (when 
        # it's set in _widget). This is useful when you open multiple 
        # plugins at once. Also if you open multiple instances of your 
        # plugin at once, these lines add number to make it easy to 
        # tell from pane to pane.
        if context.serial_number() > 1:
            self._widget.setWindowTitle(self._widget.windowTitle() + (' (%d)' % context.serial_number()))
        # Add widget to the user interface
        context.add_widget(self._widget)

        self._actions = {}

        self._timer_refresh_actions = QTimer(self)
        self._timer_refresh_actions.timeout.connect(self.refresh_actions)
        self._timer_refresh_actions.start(1000)

    @Slot()
    def refresh_actions(self):
        actions = {}
        for topic in rospy.get_published_topics():
            if "/result" in topic[0]:
                name = "/".join(topic[0].split("/")[:-1])
                msgName = topic[1]
                actionType = roslib.message.get_message_class(msgName + "Action")
                goalType = roslib.message.get_message_class(msgName + "Goal")
                actions[name] = {
                    "action": actionType,
                    "goal": goalType
                }
            
        new_actions = {}

        for action_name in actions:
                # if topic is new or has changed its type
                if action_name not in self._actions:
                    # create new TopicInfo
                    item = QTreeWidgetItem(self._widget.actions_tree_widget, [action_name])
                    new_actions[action_name] = {
                        'type': actions[action_name],
                        'item': item
                    }
                else:
                    # if topic has been seen before, copy it to new dict and
                    # remove it from the old one
                    new_actions[action_name] = self._actions[action_name]
                    del self._actions[action_name]
            
        for action_name in self._actions.keys():
            index = self._widget.actions_tree_widget.indexOfTopLevelItem(
                                        self._actions[action_name]['item'])
            self._widget.actions_tree_widget.takeTopLevelItem(index)
            del self._actions[action_name]
        
        self._actions = new_actions
        



    def shutdown_plugin(self):
        # TODO unregister all publishers here
        pass

    def save_settings(self, plugin_settings, instance_settings):
        # TODO save intrinsic configuration, usually using:
        # instance_settings.set_value(k, v)
        pass

    def restore_settings(self, plugin_settings, instance_settings):
        # TODO restore intrinsic configuration, usually using:
        # v = instance_settings.value(k)
        pass

    #def trigger_configuration(self):
        # Comment in to signal that the plugin has a way to configure
        # This will enable a setting button (gear icon) in each dock widget title bar
        # Usually used to open a modal configuration dialog