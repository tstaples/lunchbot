def getValueOrDefault(arr, key, defaultValue = None):
    if arr and key in arr:
        return arr[key]
    return defaultValue