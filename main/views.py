import os
import random
import json
import decimal
from dotenv import load_dotenv

from django.shortcuts import render
from django.db import connection
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from main.data_files.init_database import table_init
from main.canned_queries import canned_queries

load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def is_data_imported():
    table_init() # Error proofed with IF NOT EXISTS
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM crime;")
        count = cursor.fetchone()[0]
    return count > 0


def execute_query(query, page, pagination):
    per_page=30
    with connection.cursor() as cursor:
        cursor.execute(query)
        if cursor.description:
            raw_results = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
        else:
            return None, None
        if not pagination:
            return raw_results, columns
        
        # Paginate the results
        paginator = Paginator(raw_results, per_page)
        try:
            results = paginator.page(page)
        except PageNotAnInteger:
            results = paginator.page(1)
        except EmptyPage:
            results = paginator.page(paginator.num_pages)
        return results, columns

def graph(results):
    if not results:
        return {}
    labels = [row[0] for row in results]
    backgroundColor, borderColor = generate_colors(len(results))
    try:
        values = [float(row[1]) for row in results]
    except Exception:
        values = [row[1] for row in results]
    return {
        "labels": labels,
        "datasets": [{
            "label": "Count",
            "data": values,
            "backgroundColor": backgroundColor,
            "borderColor": borderColor,
            "borderWidth": 1
        }]
    }

def multi_graph(results, columns):
    if not results:
        return {}
    
    city_col, x_col, y_col = columns[:3]  # First three columns (city, X, Y)

    labels = sorted(set(row[1] for row in results))
    cities = sorted(set(row[0] for row in results))

    # Initialize dataset dictionary
    datasets = {city: [0] * len(labels) for city in cities}

    for row in results:
        city, x_value, y_value = row
        x_index = labels.index(x_value)
        datasets[city][x_index] = y_value

    backgroundColor, borderColor = generate_colors(len(cities))

    formatted_datasets = [
        {
            "label": city,
            "data": datasets[city],
            "backgroundColor": backgroundColor[idx],
            "borderColor": borderColor[idx],
            "borderWidth": 2,
            "fill": False
        }
        for idx, city in enumerate(cities)
    ]

    return {
        "labels": labels, 
        "datasets": formatted_datasets
    }

def heatmap_graph(results):
    heatmap_data = [
        {"lat": float(row[0]), "lng": float(row[1])}
        for row in results
    ]
    return heatmap_data

def generate_colors(count):
    backgroundColor = []
    borderColor = []

    for _ in range(count):
        r = random.randint(50, 220)
        g = random.randint(50, 220)
        b = random.randint(50, 220)
        backgroundColor.append(f"rgba({r}, {g}, {b}, 0.6)")
        borderColor.append(f"rgba({r}, {g}, {b}, 1)")

    return backgroundColor, borderColor

def dashboard(request):

    results = None
    columns = None
    error_message = None
    success_message = None
    graph_data = None
    graph_data_json = None
    chart_type = None
    pagination = True

    query = request.GET.get("sql_query", "")
    page = request.GET.get("page", 1)

    if request.method == "POST":
        page = 1
        # New query submitted, clear previous one
        query = request.POST.get("sql_query", "")
        request.session["last_query"] = query  # Store query in session

        canned_query = request.POST.get("canned_query" "")

        if canned_query and canned_query in canned_queries:
            query, chart_type = canned_queries[canned_query]()
            if chart_type == 'heatmap':
                pagination = False
            request.session["last_chart_type"] = chart_type

        if query:
            request.session["last_query"] = query

    elif "last_query" in request.session:
        # Preserve query across pagination clicks
        query = request.session["last_query"]
        chart_type = request.session.get("last_chart_type", None)
    if query:
        try:
            results, columns = execute_query(query, page, pagination)
            if results is None:
                success_message = "Query executed successfully."
            elif chart_type:
                if 'city' in [col.lower() for col in columns]: # Checks for 'city' column
                    graph_data = multi_graph(results, columns)
                elif chart_type == 'heatmap':
                    graph_data = heatmap_graph(results)
                else:
                    graph_data = graph(results)
        
            graph_data_json = json.dumps(graph_data, default=lambda o: float(o) if isinstance(o, decimal.Decimal) else o)
            request.session["graph_data"] = graph_data_json

        except Exception as e:
            error_message = str(e)
            results = None
            columns = None

    return render(request, "dashboard.html", {
        "results": results,
        "columns": columns if results else None,
        "error_message": error_message,
        "success_message": success_message,
        "query": query,
        "graph_data" : graph_data_json,
        "chart_type": chart_type,
        "google_maps_api_key": os.getenv("GOOGLE_MAPS_API_KEY")
    })