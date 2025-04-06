import json
import os
from datetime import datetime

from burp import IBurpExtender, IContextMenuFactory, IExtensionStateListener, ITab
from java.awt import BorderLayout, FlowLayout, Toolkit
from java.awt.datatransfer import StringSelection
from javax.swing import (
    BorderFactory,
    Box,
    BoxLayout,
    DefaultListModel,
    JButton,
    JFileChooser,
    JList,
    JMenuItem,
    JOptionPane,
    JPanel,
    JScrollPane,
    JTextField,
)


class saveMyRepeaterTab(ITab):
    def __init__(self, callbacks):
        self._callbacks = callbacks
        self.directory = "."

        self.panel = JPanel(BorderLayout())
        self.load_function = lambda path_file: None
        self.response_function = lambda path_file: None

        self.list_model = DefaultListModel()
        self.file_list = JList(self.list_model)
        scroll_pane = JScrollPane(self.file_list)
        scroll_pane.setBorder(BorderFactory.createTitledBorder("Repeater files"))

        self.directory_path = JTextField(50)
        self.directory_path.setEditable(False)
        self.directory_path.setText(self.directory)
        self.list_files(self.directory)
        self.directory_path.setBorder(
            BorderFactory.createTitledBorder("Selected folder")
        )

        self.select_button = JButton(
            "Select folder", actionPerformed=self.choose_directory
        )

        dir_panel = JPanel()
        dir_panel.setLayout(BoxLayout(dir_panel, BoxLayout.LINE_AXIS))
        dir_panel.add(self.directory_path)
        dir_panel.add(Box.createHorizontalStrut(10))
        dir_panel.add(self.select_button)

        action_panel = JPanel(FlowLayout())
        self.load_button = JButton(
            "Load the repeater tab", actionPerformed=self.load_button_action
        )
        self.response_button = JButton(
            "Copy to the clipboard the response",
            actionPerformed=self.response_button_action,
        )

        action_panel.add(self.load_button)
        action_panel.add(self.response_button)

        self.panel.add(dir_panel, BorderLayout.NORTH)
        self.panel.add(scroll_pane, BorderLayout.CENTER)
        self.panel.add(action_panel, BorderLayout.SOUTH)

        self._callbacks.addSuiteTab(self)

    def choose_directory(self, event):
        chooser = JFileChooser()
        chooser.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY)

        if chooser.showOpenDialog(None) == JFileChooser.APPROVE_OPTION:
            directory = chooser.getSelectedFile().getAbsolutePath()
            self.directory_path.setText(directory)
            self.directory = directory
            self.list_files(directory)

    def get_absolute_path_file(self, filename):
        return os.path.join(self.directory, filename)

    def list_files(self, directory):
        self.list_model.clear()
        for file in os.listdir(directory):
            if file.endswith(".json"):
                self.list_model.addElement(file[:-5])

    def load_button_action(self, event):
        selected_file = self.file_list.getSelectedValue()
        absolute_path_file = os.path.join(self.directory, selected_file + ".json")
        if selected_file:
            self.load_function(absolute_path_file)
        else:
            JOptionPane.showMessageDialog(None, "Please select a file from the list.")

    def response_button_action(self, event):
        selected_file = self.file_list.getSelectedValue()
        absolute_path_file = os.path.join(self.directory, selected_file + ".json")
        if selected_file:
            self.response_function(absolute_path_file)
        else:
            JOptionPane.showMessageDialog(None, "Please select a file from the list.")

    def getTabCaption(self):
        return "saveMyRepeater"

    def getUiComponent(self):
        return self.panel

    def setExtender(self, extender):
        self.extender = extender


class BurpExtender(IBurpExtender, IExtensionStateListener, IContextMenuFactory):
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        self._callbacks.setExtensionName("saveMyRepeater")
        self._callbacks.registerExtensionStateListener(self)
        self._callbacks.registerContextMenuFactory(self)
        self._invocation = None

        self.tab = saveMyRepeaterTab(callbacks)
        self.tab.setExtender(self)
        self.tab.load_function = self.load_repeater_tab
        self.tab.response_function = self.copy_repeater_response
        callbacks.addSuiteTab(self.tab)

        print("saveMyRepeater loaded!!!")

    def load_repeater_tab(self, save_file):
        try:
            with open(save_file, "r") as f:
                req = json.load(f)

            request_bytes = self._helpers.base64Decode(req["request"])
            http_service = self._helpers.buildHttpService(
                req["host"], req["port"], req["protocol"]
            )
            self._callbacks.sendToRepeater(
                http_service.getHost(),
                http_service.getPort(),
                req["protocol"] == "https",
                request_bytes,
                req["tabName"],
            )

            print("Loaded the repeater tab: " + save_file)

        except Exception as e:
            JOptionPane.showMessageDialog(None, "Failed to load the tab: " + str(e))

    def copy_repeater_response(self, save_file):
        try:
            with open(save_file, "r") as f:
                req = json.load(f)

            response = self._helpers.base64Decode(req["response"])
            selection = StringSelection(response.tostring())
            Toolkit.getDefaultToolkit().getSystemClipboard().setContents(
                selection, None
            )
            print("Copied to clipboard the repeater response: " + save_file)

        except Exception as e:
            JOptionPane.showMessageDialog(None, "Failed to load the tab: " + str(e))

    def _save_repeater_tab(self, tab_name):
        repeaters = self._invocation.getSelectedMessages()
        entry = repeaters[0]

        request_data = {
            "tabName": tab_name,
            "host": entry.getHttpService().getHost(),
            "port": entry.getHttpService().getPort(),
            "protocol": entry.getHttpService().getProtocol(),
            "request": self._helpers.base64Encode(entry.getRequest().tostring()),
            "response": (
                self._helpers.base64Encode(entry.getResponse().tostring())
                if entry.getResponse()
                else ""
            ),
        }

        filename = tab_name + ".json"
        absolute_path_file = self.tab.get_absolute_path_file(filename)
        if os.path.exists(absolute_path_file):
            filename = (
                tab_name + "__" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".json"
            )
        absolute_path_file = self.tab.get_absolute_path_file(filename)
        try:
            with open(absolute_path_file, "w") as f:
                json.dump(request_data, f, indent=4)
            print("Repeater tab saved:" + absolute_path_file)

        except Exception as e:
            JOptionPane.showMessageDialog(None, "Failed to save the tab: " + str(e))
        self.tab.list_files(self.tab.directory)

    def createMenuItems(self, invocation):
        self._invocation = invocation
        menu = []
        save_item = JMenuItem("Save this repeater tab", actionPerformed=self.on_save)
        menu.append(save_item)
        return menu

    def on_save(self, event):
        tab_name = JOptionPane.showInputDialog("Enter a name for the repeater tab")
        self._save_repeater_tab(tab_name)

    def extensionUnloaded(self):
        pass
