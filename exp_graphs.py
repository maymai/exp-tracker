from plotly import tools
import plotly as py
import plotly.graph_objs as go

def pie_make(graphs, filename):
    sorted_graphs = sorted(graphs)
    graph_count = len(graphs)
    if graph_count % 2 != 0:
        graph_count += 1
    g_rows = graph_count / 2
    g_cols = 3
    g_titles = list(graphs.keys())
    fig = {"data": [], "layout": {"title": filename, "showlegend": True, "annotations": []}}
    plot = [1, 1]
    for g in sorted_graphs:
        g_data = {}
        g_data["labels"] = list(graphs[g].keys())
        g_data["values"] = list(graphs[g].values())
        g_data["name"] = g
        g_data["type"] = "pie"
        g_data["hoverinfo"] = "all"
        g_data["textinfo"] = g
        gx = [((plot[1] - 1) * (1 / g_cols)) + 0.01, (plot[1] * (1 / g_cols)) - 0.01]
        gy = [1 - (((plot[0] - 1) * (1 / g_rows)) + 0.01), 1 - ((plot[0] * (1 / g_rows)) - 0.01)]
        g_data["domain"] = {"x": gx, "y": gy}
        fig["layout"]["annotations"].append({"text": g.upper(), "x": (gx[0]), "y": (gy[0]),\
            "showarrow": True, "font": {"size": 15}})
        plot[1] += 1
        if plot[1] > g_cols:
            plot[0] += 1
            plot[1] = 1
        fig["data"].append(g_data)
    py.offline.plot(fig, filename=filename+".html")
