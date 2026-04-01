from django.shortcuts import render

def index(request):
    """
    Main dashboard view. 
    Renders the layout with the Leaflet map and Sidebar.
    """
    return render(request, 'dashboard/index.html')
