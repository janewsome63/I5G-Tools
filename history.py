import variables as var

guidnum_list = []
hist_list = []
length_list = []

def add(guid, num, value):
    global guidnum_list
    global hist_list
    global length_list
    guidnum = guid + str(num)
    if not guidnum in guidnum_list:
        guidnum_list.append(guidnum)
        hist_list.append([-1]*var.settings['axis_samples'])
        length_list.append(0)
    index = guidnum_list.index(guidnum)
    hist = hist_list[index]
    length = length_list[index]

    #print("add1 ", length, hist)
    if length == var.settings['axis_samples'] and not (hist[var.settings['axis_samples']-1] == -1):
        start = 0 #index to start shifting values in hist[]
        if (hist[0] < var.settings['high_threshold'] and value >= var.settings['high_threshold']) or (hist[0] > var.settings['low_threshold'] and value <= var.settings['low_threshold']): #if the history crosses a threshold barrier in the correct direction, do not overwrite the oldest entry in hist[] to preserve that information
            start = 1
        for ind in range(start, var.settings['axis_samples']-1):
            hist[ind] = hist[ind+1]
        hist[var.settings['axis_samples']-1] = value
    else:
        if length < var.settings['axis_samples']:
            length += 1
        hist[length-1] = value
    #print("add2 ", length, hist)
    hist_list[index] = hist
    length_list[index] = length

def check_valid(guid, num, threshold, ascending):
    global guidnum_list
    global hist_list
    global length_list
    guidnum = guid + str(num)
    if not guidnum in guidnum_list:
        print("Warning: guidnum not found in list ???")
        return False
    index = guidnum_list.index(guidnum)
    hist = hist_list[index]
    length = length_list[index]
    #print("check1 ", hist)
    if length < var.settings['axis_samples']-1 or hist[var.settings['axis_samples']-1] == -1:
        #print("Check False0")
        return False
    if ascending:
        if (hist[0] < threshold) and hist[var.settings['axis_samples']-1 >= threshold]:
            #print("Check True1: ", hist[0], threshold, ascending, hist[var.settings['axis_samples']-1])
            return True
        else:
            #print("Check False1: ", hist[0], threshold, ascending, hist[var.settings['axis_samples']-1])
            return False
    else:
        if (hist[0] > threshold) and hist[var.settings['axis_samples']-1 <= threshold]:
            #print("Check True2: ", hist[0], threshold, ascending, hist[var.settings['axis_samples']-1])
            return True
        else:
            #print("Check False2: ", hist[0], threshold, ascending, hist[var.settings['axis_samples']-1])
            return False

def clear():
    global guidnum_list
    global hist_list
    global length_list
    guidnum_list = []
    hist_list = []
    length_list = []