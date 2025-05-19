import helper_methods
import gui

print("Parsing data, please wait..")  
top10MapList = helper_methods.movieMapListParse()
print("Data parsed succesfully.") 

gui.guiFunc(top10MapList)



