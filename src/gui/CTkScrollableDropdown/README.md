# CTkScrollableDropdown
Replace the old looking tkMenu and add this new scrollable dropdown menu to customtkinter **optionmenu, combobox, entries, buttons** etc...

## Features
- Rounded corners
- **Define custom height for the menu**
- Automatic resize
- Transparency effects
- **Autocomplete options**
- Full customisability
- Add images to options
- Automatic bindings added for ctkoptionmenu/ctkcombobox

![Platform](https://img.shields.io/powershellgallery/p/Pester?color=blue)

![screenshots](https://user-images.githubusercontent.com/89206401/236677843-8d8b76fd-6145-47b1-8f4d-b6a64b08e1ea.png)

## Installation
### [<img alt="GitHub repo size" src="https://img.shields.io/github/repo-size/Akascape/CTkScrollableDropdown?&color=white&label=Download%20Source%20Code&logo=Python&logoColor=yellow&style=for-the-badge"  width="400">](https://github.com/Akascape/CTkScrollableDropdown/archive/refs/heads/main.zip)

**Download the source code, paste the `CTkScrollableDropdown` folder in the directory where your program is present.**

Note: this type of dropdown was discontinued from ctk because of some tkinter OS-related bugs. But I have tried to fix them by experimenting with different window attributes. 
Current Status:
Windows: ✅ 
Linux: ✅
Mac OS: ⚠️ (random crashes can happen, help wanted)

## Simple Usage
```python
CTkScrollableDropdown(attach=widget_name, values=option_list)
```

## Full Example
```python
from CTkScrollableDropdown import *
import customtkinter

root = customtkinter.CTk()

customtkinter.CTkLabel(root, text="Different Dropdown Styles").pack(pady=5)

# Some option list
values = ["python","tkinter","customtkinter","widgets",
          "options","menu","combobox","dropdown","search"]

# Attach to OptionMenu 
optionmenu = customtkinter.CTkOptionMenu(root, width=240)
optionmenu.pack(fill="x", padx=10, pady=10)

CTkScrollableDropdown(optionmenu, values=values)

# Attach to Combobox
combobox = customtkinter.CTkComboBox(root, width=240)
combobox.pack(fill="x", padx=10, pady=10)

CTkScrollableDropdown(combobox, values=values, justify="left", button_color="transparent")

# Attach to Entry
customtkinter.CTkLabel(root, text="Live Search Values").pack()

entry = customtkinter.CTkEntry(root, width=240)
entry.pack(fill="x", padx=10, pady=10)

CTkScrollableDropdown(entry, values=values, command=lambda e: entry.insert(1, e),
                      autocomplete=True) # Using autocomplete

# Attach to Button 
button = customtkinter.CTkButton(root, text="choose options", width=240)
button.pack(fill="x", padx=10, pady=10)

CTkScrollableDropdown(button, values=values, height=270, resize=False, button_height=30,
                      scrollbar=False, command=lambda e: button.configure(text=e))

root.mainloop()
```

## Arguments
| Parameter | Description |
|-----------| ------------|
| **attach** | parent widget to which the dropdown menu will be attached  |
| x | **optional**, change the horizontal offset of the widget manually  |
| y | **optional**, change the vertical offset of the widget manually |
| width | **optional**, change the default width of the menu |
| height | **optional**, change the default height of the menu |
| **values** | add the list of options in the dropdown menu |
| image_values | **optional**, add list of images in options |
| **fg_color** | change the fg_color of the scrollable frame |
| button_color | change the fg_color of the buttons/options |
| hover_color | change the hover_color of the buttons/options |
| text_color | change the text_color of the buttons/options |
| button_height | change the height of the buttons if required
| **autocomplete** | add live search options for ctkcombobox or ctkentry widget |
| **alpha** | change the transparency of the whole dropdown widget (range: 0-1) |
| justify | change the anchor of the option text |
| corner | adjust roundness of the frame corners |
| double_click | bind double click for menu popup |
| resize | resize the menu dynamically, default: True |
| frame_border_width | change the border_width of the frame if required |
| frame_border_color | change the border_color of the frame |
| scrollbar | hide the scrollbar if required, default: True |
| command | add the command when option is selected |
| _*Other Parameters_ | _All other parameters for ctkbutton or scrollbar can be passed in dropdownmenu_ |

## Methods
- **.insert(value="new_option", ...)**
  
  Add a new option to the list
- **.configure(values=new_values, height=500, ...)**

  Update some parameters for the dropdown
- **.live_update(string="option")**

  filter options dynamically
- **.destroy_popup()**

  Remove the dropdown completely
- **.popup(x, y)**

  Show popup menu manually

Note: if you are facing some issues then try using the `CTkScrollableDropdownFrame`.
