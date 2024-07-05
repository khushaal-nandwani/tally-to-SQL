## Q1. why is the parameter window important in countNumberOfInstance in utils.au3 function? given below
```
Func CountNumberOfInstances($className, $window)
    Local $count = 0
    Local $instance = 1
    Do  
        If $className == "lblCaption" Then
            $instanceName = "[NAME:" & $className & "; INSTANCE:" & $instance & "]"
        Else
            $instanceName = "[CLASS:" & $className & "; INSTANCE:" & $instance & "]"
        EndIf
        If ControlCommand($window, "", $instanceName, "IsVisible", "") Then
            $count += 1
        Else
            ExitLoop
        EndIf
        $instance += 1
    Until 0
    Return $count
EndFunc
```
## Q2. How many seconds will ImplicitWait function will wait before it exits the do while loop early?
```
Func ImplicitWait($Title, $ControlID, $Status, $ExpectedValue)
    Local $time = 0
    Do
        $time += 1
        If $time >= 800 Then 
            ExitLoop
        EndIf
        Sleep(10)
    Until ControlCommand($Title, "", $ControlID, $Status) = $ExpectedValue
 EndFunc 
```


## Q3. Below is Area0.au3. How can we improve the quality of the following code?
```
#include <..\..\Common\Utils.au3>
#include <Area_Constants.au3>
#include <Area_Data.au3>

WinWaitActive($RadixWindow)
OpenMenu()

$Criteria = "Checks the number of instances of buttons, textboxes and labels"

ImplicitWait($RadixWindow, $FormAreaTitleCID, 'IsVisible', 1)
$numberOfButtonInstances = CountNumberOfInstances($ButtonClass, $RadixWindow)
If Not $numberOfButtonInstances = $ExpectedNumberOfButtons Then
    WriteMyLog("Invalid Count", "Buttons", $ExpectedNumberOfButtons, $numberOfButtonInstances)
EndIf

$numberOfTextBoxInstances = CountNumberOfInstances($TextBoxClass, $RadixWindow)
If Not $numberOfTextBoxInstances = $ExpectedNumberOfTextBoxes Then
    WriteMyLog("Invalid Count", "TextBoxes", $ExpectedNumberOfTextBoxes, $numberOfTextBoxInstances)
EndIf

$numberOfLabelInstances = CountNumberOfInstances($LabelClass, $RadixWindow)
If Not $numberOfLabelInstances = $ExpectedNumberOfLabels Then
    WriteMyLog("Invalid Count", "Labels", $ExpectedNumberOfLabels, $numberOfLabelInstances)
EndIf

ClickButton($CloseButton, "Close Button")
```

## Q4. idName and odName has same values, was it necessary to define it twice under Area_Data.au3? Explain why 
```
;~ Input Data
$idName = 'SANJAY NAGAR'

;~ Output Data
$odAreaCode = 'SANJAYNAGA'
$odName = 'SANJAY NAGAR'
```