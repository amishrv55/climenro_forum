from django.shortcuts import render, redirect
from .models import PolicyNode
from .utils import classify_policy, build_policy_node, load_activity_table, load_country_factors
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
import networkx as nx

activity_df = load_activity_table()
country_df = load_country_factors()

def add_policy_view(request):
    context = {
        'step': 1,
        'countries': sorted(country_df["Country"].unique()),
    }

    if request.method == "POST":
        step = int(request.POST.get("step", 1))

        if step == 1:
            # Step 1: User submitted policy text
            policy_text = request.POST.get("policy_text")
            country = request.POST.get("country")
            intent = request.POST.get("intent")
            title = request.POST.get("title")
            date_issued = request.POST.get("date_issued")

            result = classify_policy(policy_text, activity_df)

            if result["matched"]:
                activity_row = activity_df.iloc[result["match_index"]]
                input_type = activity_row["Required Input Type"].lower()
                uses_displacement = activity_row["Uses Displacement"] == "TRUE"
                context.update({
                    "step": 2,
                    "input_type": input_type,
                    "policy_text": policy_text,
                    "country": country,
                    "intent": intent,
                    "title": title,
                    "date_issued": date_issued,
                })
                return render(request, "policy_graph/add_policy_step2.html", context)
            else:
                context["error"] = "Policy not matched with any activity."
                return render(request, "policy_graph/add_policy_step1.html", context)

        elif step == 2:
            # Step 2: User submitted input value
            input_val = float(request.POST.get("user_input"))
            policy_text = request.POST.get("policy_text")
            country = request.POST.get("country")
            intent = request.POST.get("intent")
            title = request.POST.get("title")
            date_issued = request.POST.get("date_issued")

            policy_node = build_policy_node(policy_text, country, input_val, 5000, activity_df, country_df)

            if policy_node:
                PolicyNode.objects.create(
                    policy_node=policy_node["Policy Node"],
                    policy_title=title,
                    country=country,
                    date=datetime.strptime(date_issued, "%Y-%m-%d").date(),
                    graph_intent=intent,
                    sector=policy_node.get("Sector"),
                    co2_impact=policy_node.get("CO₂ Impact (Mt ±)", 0),
                    alignment=policy_node.get("Alignment"),
                    instrument=policy_node.get("Instrument"),
                    start_end=policy_node.get("Start–End"),
                    beneficiary=policy_node.get("Beneficiary"),
                    influencer=policy_node.get("Influencer"),
                    efficiency=policy_node.get("Efficiency"),
                    node_size=policy_node.get("Node Size"),
                    node_color=policy_node.get("Node Color"),
                    original_text=policy_text,
                )
                return redirect("policy_graph:graph_view")
            else:
                context["error"] = "Failed to generate policy node."
                return render(request, "policy_graph/add_policy_step1.html", context)

    return render(request, "policy_graph/add_policy_step1.html", context)



def graph_view(request):
    intent_filter = request.GET.get('intent')
    country_filter = request.GET.get('country')

    nodes = PolicyNode.objects.all()

    if intent_filter:
        nodes = nodes.filter(graph_intent=intent_filter)
    if country_filter:
        nodes = nodes.filter(country=country_filter)

    if not nodes.exists():
        return render(request, 'policy_graph/graph_view.html', {
            'error': 'No policies found to render the graph.',
            'available_intents': PolicyNode.objects.values_list('graph_intent', flat=True).distinct(),
            'available_countries': PolicyNode.objects.values_list('country', flat=True).distinct(),
            'current_intent': intent_filter,
            'current_country': country_filter
        })

    # Build graph
    G = nx.DiGraph()

    for node in nodes:
        G.add_node(
        node.policy_node,
        size=node.node_size,
        color=node.node_color,
        impact=node.co2_impact,
        title=node.policy_title,
        country=node.country,
        date=node.date.strftime('%Y-%m-%d'),
        sector=node.sector,
        alignment=node.alignment
        )
        G.add_edge(node.graph_intent, node.policy_node)


    pos = nx.spring_layout(G, k=0.5, iterations=50)

    # Plotly edges
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1.5, color='#888'),
        hoverinfo='none',
        mode='lines'
    )

    # Plotly nodes
    node_x, node_y, node_text, node_size, node_color, customdata = [], [], [], [], [], []

    for node in G.nodes():
        x, y = pos[node]
        node_data = G.nodes[node]
        node_x.append(x)
        node_y.append(y)
        node_size.append(node_data.get('size', 20) * 2)
        node_color.append(node_data.get('color', 'gray'))
        customdata.append([node_data.get('impact', 0), node_data.get('title', 'N/A')])

        text = f"<b>{node}</b><br>Title: {node_data.get('title')}<br>Country: {node_data.get('country')}<br>Impact: {node_data.get('impact')} Mt CO₂<br>Sector: {node_data.get('sector')}<br>Date: {node_data.get('date')}"
        node_text.append(text)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        textposition='top center',
        hoverinfo='text',
        marker=dict(
            showscale=False,
            color=node_color,
            size=node_size,
            line_width=2,
            line_color='DarkSlateGrey'
        ),
        text=[n if len(n) < 20 else n[:17] + "..." for n in G.nodes()],
        hovertext=node_text
    )

    fig = go.Figure(data=[edge_trace, node_trace],
        layout=go.Layout(
            title='🌐 National Policy Graph',
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=650
        )
    )

    fig_html = fig.to_html(full_html=False)

    return render(request, 'policy_graph/graph_view.html', {
        'graph_html': fig_html,
        'available_intents': PolicyNode.objects.values_list('graph_intent', flat=True).distinct(),
        'available_countries': PolicyNode.objects.values_list('country', flat=True).distinct(),
        'current_intent': intent_filter,
        'current_country': country_filter
    })
