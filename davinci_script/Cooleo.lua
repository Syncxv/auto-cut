local ui = fu.UIManager
local disp = bmd.UIDispatcher(ui)

local winID = "Cooleo"

local projectManager = resolve:GetProjectManager()
local project = projectManager:GetCurrentProject()
local mediaPool = project:GetMediaPool()

local platform = (FuPLATFORM_WINDOWS and "Windows") or
    (FuPLATFORM_MAC and "Mac") or
    (FuPLATFORM_LINUX and "Linux")

local function script_path()
    return debug.getinfo(2, "S").source:sub(2)
end

local function ScriptIsInstalled()
    local script_path = script_path()
    if platform == "Windows" then
        local match1 = script_path:find("\\Blackmagic Design\\DaVinci Resolve\\Support\\Fusion\\Scripts")
        local match2 = script_path:find("\\Blackmagic Design\\DaVinci Resolve\\Fusion\\Scripts")
        return match1 ~= nil or match2 ~= nil
    elseif platform == "Mac" then
        local match1 = script_path:find("/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts")
        return match1 ~= nil
    else
        local match1 = script_path:find("resolve/Fusion/Scripts")
        local match2 = script_path:find("resolve/Fusion/Scripts")
        local match3 = script_path:find("/DaVinciResolve/Fusion/Scripts")
        return match1 ~= nil or match2 ~= nil or match3 ~= nil
    end
end

local SCRIPT_INSTALLED = ScriptIsInstalled()


local COLUMN_WIDTH = 130
local WINDOW_WIDTH = 320
local WINDOW_HEIGHT = 356

local PRIMARY_ACTION_BUTTON_CSS = [[
    QPushButton
    {
        border: 1px solid rgb(51,176,74);
        max-height: 28px;
        border-radius: 14px;
        background-color: rgb(51,176,74);
        color: rgb(255, 255, 255);
        min-height: 28px;
        font-size: 13px;
    }
    QPushButton:hover
    {
        border: 2px solid rgb(40,140,59);
        background-color: rgb(40,140,59);
    }
    QPushButton:pressed
    {
        border: 2px solid rgb(36,126,53);
        background-color: rgb(36,126,53);
    }
    QPushButton:!enabled
    {
        border: 2px solid rgb(36,126,53);
        background-color: rgb(36,126,53);
        color: rgb(150, 150, 150);
    }
]]

local SECONDARY_ACTION_BUTTON_CSS = [[
    QPushButton
    {
        max-height: 24px;
        min-height: 24px;
    }
]]

local DIVIDER_CSS = [[
    QFrame[frameShape="4"]
    {
        border: none;
        background-color: rgb(30, 30, 30);
        max-height: 1px;
    }
]]
local COMBOBOX_PLACEHOLDER_CSS = [[
    QLabel
    {
        color: rgb(140, 140, 140);
        font-size: 13px;
        min-height: 26px;
        max-height: 26px;
        background-color: rgb(31,31,31);
        border: 1px solid rgb(0,0,0);
        border-top-right-radius: 0px;
        border-bottom-right-radius: 0px;
        border-top-left-radius: 4px;
        border-bottom-left-radius: 4px;
        padding-left: 4px;
    }
]]
local COMBOBOX_ACTION_BUTTON_CSS = [[
    QPushButton
    {
        border: 1px solid rgb(0,0,0);
        border-top-right-radius: 4px;
        border-bottom-right-radius: 4px;
        border-top-left-radius: 0px;
        border-bottom-left-radius: 0px;
        border-left: 0px;
        font-size: 22px;
        min-height: 26px;
        max-height: 26px;
        min-width: 26px;
        max-width: 26px;
        background-color: rgb(31,31,31);
    }
    QPushButton:hover
    {
        color: rgb(255, 255, 255);
    }
    QPushButton:pressed
    {
        background-color: rgb(20,20,20);
    }
]]
local SECTION_TITLE_CSS = [[
    QLabel
    {
        color: rgb(255, 255, 255);
        font-size: 13px;
        font-weight: bold;
    }
    QLabel:!enabled
    {
        color: rgb(150, 150, 150);
    }
]]
local function OpenURL(url)
    if bmd.openurl then
        bmd.openurl(url)
        print("[Opening URL] " .. url)
    end
end


local function ClearTable(table)
    for k in pairs(table) do
        table[k] = nil
    end
end


local function EndDispLoop()
    local win = ui:FindWindow(winID)
    if win ~= nil then
        return
    end

    disp:ExitLoop()
end


local function CreateDialog(title, message)
    local position = {nil, nil}
    local win = ui:FindWindow(winID)
    if win ~= nil then
        position = {win.Geometry[1] + 10, win.Geometry[2] + 150}
    end

    local dialog = disp:AddWindow({
        ID = "SnapCaptionsDialog",
        WindowTitle = "Cooleo | Error",
        WindowModality = "ApplicationModal",
        Geometry = {position[1], position[2], 300, 100},
        FixedSize = {300, 100},
        Margin = 16,
        ui:VGroup
        {
            ID = "root",
            Spacing = 4,
            FixedX = 300,
            FixedY = 100,
            ui:Label
            {
                Weight = 0,
                ID = "error_title",
                Text = title,
                Alignment = { AlignHCenter = true, AlignBottom = true},
                WordWrap = true,
                StyleSheet = [[
                    QLabel {
                        color: rgb(255, 255, 255);
                        font-size: 13px;
                        font-weight: bold;
                    }
                ]]
            },
            ui:Label
            {
                Weight = 10,
                ID = "error_message",
                Text = message,
                WordWrap = true,
                Alignment = { AlignHCenter = true, AlignTop = true }
            },
            ui:VGap(0, 1),
            ui:HGroup
            {
                Weight = 0,
                ui:Button{ ID = "OK",
                            Text = "OK",
                            StyleSheet = SECONDARY_ACTION_BUTTON_CSS
                }
            }
        }
    })

    function dialog.On.OK.Clicked(ev)
        dialog:Hide()
        dialog = nil
        EndDispLoop()
    end

    function dialog.On.SnapCaptionsDialog.Close(ev)
        dialog:Hide()
        dialog = nil
        EndDispLoop()
    end

    return dialog
end


local function CopyFile(source, target)
    local source_file = io.open(source, "r")
    local contents = source_file:read("*a")
    source_file:close()

    local target_file = io.open(target, "w")
    if target_file == nil then
        return false
    end
    target_file:write(contents)
    target_file:close()

    return true
end


local function InstallScript()
    local source_path = script_path()
    local target_path = nil
    local modules_path = nil
    if platform == "Windows" then
        target_path = os.getenv("APPDATA") .. "\\Blackmagic Design\\DaVinci Resolve\\Support\\Fusion\\Scripts\\Comp\\"
        modules_path = os.getenv("APPDATA") .. "\\Blackmagic Design\\DaVinci Resolve\\Support\\Fusion\\Modules\\Lua\\"
    elseif platform == "Mac" then
        target_path = os.getenv("HOME") .. "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Comp/"
        modules_path = os.getenv("HOME") .. "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Modules/Lua/"
    else
        target_path = os.getenv("HOME") .. "/.local/share/DaVinciResolve/Fusion/Scripts/Comp/"
        modules_path = os.getenv("HOME") .. "/.local/share/DaVinciResolve/Fusion/Modules/Lua/"
    end

    local script_name = source_path:match(".*[/\\](.*)")
    target_path = target_path .. script_name

    -- Copy the file.
    local success = CopyFile(source_path, target_path)
    if not success then
        local dialog = CreateDialog("Failed to install Cooleo",
            "Cooleo could not be installed automatically. " ..
            "Please manually copy to the Scripts/Comp folder.")
        dialog:Show()
        dialog:RecalcLayout()
        return false
    end

    print("[Cooleo] Installed to " .. target_path)
    return true
end

local fusion_titles = {}
local TEXT_TEMPLATE_FOLDER = "Timestamps"
local function PopulateTextTemplates(win)
    ClearTable(fusion_titles)
    local combobox = win:Find("title_templates")
    local title_stack = win:Find("title_stack")
    local title_placeholder = win:Find("title_placeholder")
    combobox:Clear()

    local template_folder = nil
    for i, subfolder in ipairs(mediaPool:GetRootFolder():GetSubFolderList()) do
        if subfolder:GetName() == TEXT_TEMPLATE_FOLDER then
            template_folder = subfolder
            break
        end
    end

    if template_folder == nil or #template_folder:GetClipList() == 0 then
        if template_folder == nil then
            title_placeholder:SetText("No '" .. TEXT_TEMPLATE_FOLDER .. "' Bin Found")
        else
            title_placeholder:SetText("No Text+ Templates Found")
        end

        title_stack:SetCurrentIndex(1)
        combobox:SetEnabled(false)
        combobox:SetVisible(false)
        title_placeholder:SetVisible(true)
        return
    end

    title_stack:SetCurrentIndex(0)
    combobox:SetEnabled(true)
    title_placeholder:SetVisible(false)
    combobox:SetVisible(true)
    for i, clip in ipairs(template_folder:GetClipList()) do
        table.insert(fusion_titles, clip)
        combobox:AddItems({clip:GetClipProperty("Clip Name")})
    end
end

local function CreateToolWindow()
    local win = disp:AddWindow(
        {
            ID = winID,
            WindowTitle = "Cooleo",
            Geometry = {nil, nil, WINDOW_WIDTH, WINDOW_HEIGHT},
            Margin = 16,

            ui:VGroup {
                Spacing = 0,
                ui:VGroup {
                    Weight = 0,
                    ID = "install_bar",
                    Spacing = 0,
                },

                ui:VGroup {
                    ID = "root",
                    Spacing = 4,
                    FixedX = WINDOW_WIDTH,
                    FixedY = WINDOW_HEIGHT,
                    ui:Label {
                        Weight = 0,
                        ID = "title",
                        Text = "Cooleo",
                        Alignment = {AlignHCenter = true, AlignBottom = true},
                        WordWrap = true,
                        StyleSheet = [[
                            QLabel {
                                color: rgb(255, 255, 255);
                                font-size: 24px;
                                font-weight: bold;
                            }
                        ]]
                    },
                    ui:VGap(24, 0),
                    ui:Label
                    {
                        Text = "Timestamps",
                        StyleSheet = SECTION_TITLE_CSS,
                    },
                    ui:VGap(8, 0),
                    ui:HGroup
                    {
                        Spacing = 0,
                        ui:Stack
                        {
                            ID = "title_stack",
                            CurrentIndex = 0,
                            ui:ComboBox
                            {
                                ID = "title_templates",
                                MinimumSize = {10, 26}
                            },
                            ui:Label
                            {
                                ID = "title_placeholder",
                                Visible = false,
                                Text = "No '" .. TEXT_TEMPLATE_FOLDER .. "' Bin Found",
                                ToolTip = "<qt>Add Text+ templates to the Media Pool in a Bin named '" .. TEXT_TEMPLATE_FOLDER .. "'</qt>",
                                StyleSheet = COMBOBOX_PLACEHOLDER_CSS
                            }
                        },
                        ui:Button
                        {
                            ID = "refresh_text_templates",
                            Text = "↺",
                            ToolTip = "Refresh Text+ Template List",
                            StyleSheet = COMBOBOX_ACTION_BUTTON_CSS
                        }
                    },
                    ui:VGap(16, 0),
                    ui:VGroup {
                        Weight = 0,
                        ID = "start_bar",
                        Spacing = 0,

                        ui:HGroup {
                            ui:Button {
                                ID = "start_button",
                                Text = "Start",
                                StyleSheet = PRIMARY_ACTION_BUTTON_CSS
                            }
                        }
                    },
                    
                }
            }
        }
    )

    if not SCRIPT_INSTALLED then
        local content = win:GetItems().install_bar
        content:AddChild(
            ui:VGroup {
                ID = "install_group",
                Spacing = 10,
                Weight = 0,
                ui:HGroup {
                    ui:Button {
                        ID = "install_button",
                        Text = "Install",
                        StyleSheet = SECONDARY_ACTION_BUTTON_CSS
                    },

                    ui:Label {
                        Weight = 0,
                        FrameStyle = 4,
                        StyleSheet = DIVIDER_CSS
                    }
                }
            }
        )
    end

    PopulateTextTemplates(win)

    function win.On.Cooleo.Close(ev)
        disp:ExitLoop()
    end

    function win.On.install.Clicked(ev)
        local success = InstallScript()
        if not success then
            return
        end

        local content = win:GetItems().install_bar
        content:RemoveChild("install_group")
        win:RecalcLayout()
    end

    function win.On.refresh_text_templates.Clicked(ev)
        PopulateTextTemplates(win)
    end

    function win.On.start_button.Clicked(ev)
        local text_template_index = win:Find("title_templates").CurrentIndex + 1
        if text_template_index == 0 then
            local dialog = CreateDialog("No Timestaps Found",
                                        "Please add a Timestamp template to the Media Pool in a bin named '" .. TEXT_TEMPLATE_FOLDER .. "' and try again.")
            dialog:Show()
            dialog:RecalcLayout()
            return false
        end

        local item = fusion_titles[text_template_index]
        print(item:GetClipProperty("File Path"))
    end

    win:RecalcLayout()
    win:Show()
    disp:RunLoop()
    win:Hide()
end

local function Main()
    print("HI")
    -- Check that there is a current timeline.
    if project:GetCurrentTimeline() == nil then
        local dialog = CreateDialog("No Current Timeline",
                                    "Please open a timeline and try again.")
        dialog:RecalcLayout()
        dialog:Show()
        disp:RunLoop()
        return
    end

    -- If the window is already being shown, raise it and exit.
    local win = ui:FindWindow(winID)
    if win ~= nil then
        win:RecalcLayout()
        win:Show()
        win:Raise()
        return
    end

    -- Otherwise, create the tool window.
    CreateToolWindow()
end


local success, error = pcall(Main)
if not success then
    print(error)
end
