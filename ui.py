import glob
import json
import re
from collections import Counter, defaultdict
from uuid import uuid4

import pandas as pd
import streamlit as st

ESG_MAPPING = {"E": "Environment", "S": "Social", "G": "Governance"}


st.title("GatherGov ESG Intelligence")


municipality_data = {}

files = glob.glob("./small_v1_*.json")
for file in files:
    data = json.load(open(file, "r"))
    municipality_data.update(data)


cities_states = {
    "Pittsburg": "Pittsburgh, PA",
    "Davenport": "Davenport, IA",
    "Bettendorf": "Bettendorf, IA",
    "Fort Worth": "Fort Worth, TX",
    "Ann Arbor": "Ann Arbor, MI",
    "Pawtucket": "Pawtucket, RI",
    # "Prince George": "Prince George, VA",
    "Metuchen": "Metuchen, NJ",
    "Rock Island": "Rock Island, IL",
    "Moline": "Moline, IL",
    "Phoenix": "Phoenix, AZ",
    "Dallas": "Dallas, TX",
}

# municipality_data = {cities_states[m]: v for m, v in municipality_data.items()}
municipality_data = {cities_states[x]: municipality_data[x] for x in cities_states}
municipalities = sorted(municipality_data.keys())


municipality = st.sidebar.selectbox("Select Municipality", list(municipalities))
selected_municipality_data = municipality_data[municipality]

entities = defaultdict(lambda: defaultdict(list))
table_data = []
indices2chunk = {}
indices2url = {}

for index_i, transcript in enumerate(selected_municipality_data):
    for index_j, chunk in enumerate(transcript["chunks"]):
        text = chunk["text"]
        indices2chunk[(index_i, index_j)] = text
        indices2url[(index_i, index_j)] = chunk["chunk_url"]
        date = transcript["date"]
        meeting_name = " ".join(re.split("[\W_]+", transcript["meeting_name"]))
        esg_insights = chunk["esg_v2"]
        # st.write(esg_insights)
        # if not esg_insights:
        #     continue

        for entity in esg_insights:
            name = entity["name"]
            insights = entity["insights"]
            for insight in insights:
                observation = insight["observation"]
                classification = insight["classification"]
                sentiment = insight["sentiment"]
                if classification not in ESG_MAPPING:
                    continue
                entities[name][ESG_MAPPING[classification]].append(
                    (observation, date, meeting_name, sentiment, (index_i, index_j))
                )
                table_data.append(
                    (
                        name,
                        ESG_MAPPING[classification],
                        observation,
                        date,
                        meeting_name,
                        sentiment,
                        (index_i, index_j),
                    )
                )
    break

# # entity_search_tab,
# table_view_tab, reference_text_view = st.tabs(
#     [
#         # "Entity Search",
#         "Table View",
#         "Reference Text View",
#     ]
# )


# with table_view_tab:
#     table_view_tab.subheader("Viewing all the insights in tabular format.")
#     st.dataframe(
#         pd.DataFrame(
#             table_data,
#             columns=[
#                 "Entity",
#                 "Classification",
#                 "Observation",
#                 "Date",
#                 "Meeting Name",
#                 "Sentiment",
#                 "Chunk Index",
#             ],
#         )
#     )

# with entity_search_tab:
#     entity_to_display = st.selectbox(
#         label="Search entity to view insights",
#         options=entities.keys(),
#         # index=None,
#         # placeholder="Start typing to select an entity",
#     )
#     if entity_to_display:
#         entity_insights = entities[entity_to_display]
#         entity_table = []
#         for key, value in entity_insights.items():
#             for val in value:
#                 entity_table.append((key, *val))
#         st.table(
#             pd.DataFrame(
#                 entity_table,
#                 columns=[
#                     "Classification",
#                     "Observation",
#                     "Date",
#                     "Meeting Name",
#                     "Sentiment",
#                     "Chunk Index",
#                 ],
#             )
#         )

# with reference_text_view:
reference_entity_to_display = st.selectbox(
    label="Search entity to view insights and references",
    options=entities.keys(),
    # index=None,
    # placeholder="Start typing to select an entity",
)
if reference_entity_to_display:
    entity_insights = entities[reference_entity_to_display]
    entity_table = []
    for key, value in entity_insights.items():
        for val in value:
            entity_table.append((key, *val))

    for et_index, et in enumerate(entity_table):
        (
            classification,
            observation,
            date,
            meeting_name,
            sentiment,
            (index_i, index_j),
        ) = et
        chunk = indices2chunk[(index_i, index_j)]
        chunk_url = indices2url[(index_i, index_j)]
        with st.expander(
            # f" {classification} related observation with {sentiment} sentiment    ... click to expand.",
            f" Click to expand insight {et_index+1}",
            expanded=True,
        ):
            # st.subheader(f"Observation")
            st.text_area(
                "Observation",
                value=observation,
                disabled=True,
                # height=200,
                key=str(uuid4()),
            )
            # st.text_area for classification, date, meeting name, sentiment
            items_to_display = [
                ("Classification", classification),
                ("Date", date),
                ("Meeting Name", meeting_name),
                ("Sentiment", sentiment),
            ]
            for name, value in items_to_display:
                st.text_input(
                    label=name,
                    value=value,
                    disabled=True,
                    # height=20,
                    key=str(uuid4()),
                )

            st.text_area(
                label=f"Reference text: ",
                value=chunk,
                disabled=True,
                height=200,
                key=str(uuid4()),
            )
            st.write(f"Reference URL: {chunk_url}")
