import streamlit as st
import time
import pandas as pd
from collections import defaultdict as dd
from get_properties_from_pubchem import getPropertiesFromPubchem

########################################################################################################################################################
#                                                            Page Setup                                                                                #
########################################################################################################################################################

st.set_page_config(
    page_title="ChemFetchTool",
    page_icon="favicon.png",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={'About': "Retrieve molecular properties of a molecule"})

col1, col2 = st.columns([0.4, 0.6], gap="medium")
with col1:
  st.title(":rainbow[ChemFetchTool]")
with col2:
  st.image("favicon.png", width=420, use_column_width=False)
  st.subheader(":rainbow[From molecule names to properties]")

########################################################################################################################################################
#                                                            Sidebar                                                                                   #
########################################################################################################################################################

uploaded_file_df = None
uploaded_names = None

with st.sidebar:
  st.write("## :blue[Paste your compound names here] :red[(Must be one per line)]")
  uploaded_names = st.text_area("Paste your compound names here", value=None, height=105, max_chars=None, 
                                placeholder="E.g.\nCycloheterophyllin\nArtonin A\nGinkgetin",
                                label_visibility="collapsed")

  st.write("## :blue[Or Choose a file] :red[(Must be a CSV or TXT file)]")
  uploaded_file = st.file_uploader("Or Choose a file", type=['csv', 'txt'], label_visibility="collapsed")

  if uploaded_file is not None:
    uploaded_file_df = pd.read_csv(uploaded_file)
    col_names = uploaded_file_df.columns.tolist()
    st.write("### :blue[Select Column with molecule names]")
    mol_names = st.radio("Select Column with molecule names", col_names, index=None, horizontal=True, 
                         label_visibility="collapsed")
  
  st.write("## :blue[Check the properties to be retrieved]")
  col1, col2 = st.columns([1, 1])
  IS = col1.checkbox("IsomericSMILES", value=False,  label_visibility="visible")
  CS = col2.checkbox("CanonicalSMILES", value=False,  label_visibility="visible")
  MW = col1.checkbox("MolecularWeight", value=False,  label_visibility="visible")
  RBC = col2.checkbox("RotatableBondCount", value=False,  label_visibility="visible")


  properties = []
  if IS:
    properties.append("IsomericSMILES")
  if CS:
    properties.append("CanonicalSMILES")
  if MW:
    properties.append("MolecularWeight")
  if RBC:
    properties.append("RotatableBondCount")
  
  properties_string = ",".join(properties)

  col1, col2, col3 = st.columns([1, 1, 1])
  button = col2.button("Retrieve Properties", type="primary")
  # col1.button('Rerun')

st.divider()


def retrieveProperties(df, mol_col, properties):
  progress_text = "Operation in progress. Please wait. ⏳"
  total_items = len(df)
  completed_items = 0
  my_progress_bar = st.progress(0)
  status_text = st.empty()

  retrieved_properties = dd(list)
  for name in df[mol_col]:
    retrieved_properties[mol_col].append(name)
    for prop in properties:
      retrieved_properties[prop].append(getPropertiesFromPubchem(name, prop))
    completed_items += 1
    progress = int((completed_items / total_items) * 100)
    my_progress_bar.progress(progress)
    status_text.text(f"{progress_text} {progress}%")
  status_text.text("Operation complete! ⌛")
  my_progress_bar.empty()
  retrieved_properties_df = pd.DataFrame(retrieved_properties)
  return retrieved_properties_df



# def retrieveProperties(df, mol_col, properties):
#   retrieved_properties = dd(list)
#   for name in df[mol_col]:
#     retrieved_properties[mol_col].append(name)
#     for prop in properties:
#       retrieved_properties[prop].append(getPropertiesFromPubchem(name, prop))
#   retrieved_properties_df = pd.DataFrame(retrieved_properties)
#   return retrieved_properties_df

def addSNoAsIndex(df):
    df_len = len(df)
    df["S/No"] = range(1, df_len+1)
    df = df.set_index("S/No")
    return df

if button:
  try:
    if uploaded_file_df is not None and uploaded_names is not None:
      st.warning("#### Paste the molecules names or submit a molecule file not both")
    
    elif uploaded_file_df is None and uploaded_names is None:
      st.warning("#### Compound names or molecule file MUST be provided but NOT both")

    elif uploaded_names is not None:
      if properties_string != "":
        uploaded_names =  uploaded_names.strip(" ,:;.''").split("\n")
        uploaded_names_df = pd.DataFrame(uploaded_names, columns=["Compound"])
        with st.spinner("Wait for your results. You may take a walk while :rainbow[ChemFetchTool] retrieve the selected properties..."):
          retrieved_properties_df = retrieveProperties(uploaded_names_df, "Compound", properties)
        retrieved_properties_df = addSNoAsIndex(retrieved_properties_df)
        st.write(retrieved_properties_df)
      else:
        st.warning("#### At least one properties must be selected")

    elif uploaded_file_df is not None:
      if mol_names is not None and properties_string != "":
        with st.spinner("### Wait for your results. You may take a walk while :rainbow[ChemFetchTool] retrieve the selected properties..."):
          retrieved_properties_df = retrieveProperties(uploaded_file_df, mol_names, properties)
        retrieved_properties_df = addSNoAsIndex(retrieved_properties_df)
        st.write(retrieved_properties_df)
      else:
        st.warning("#### Both molecule column and at least one properties must be selected")
  except:
    st.warning("#### An unknown error occured")

st.divider()

st.write("""
Scientific articles often list compounds with interesting pharmacological effects, but only by name. This poses a problem for researchers who 
need a computer-readable format to analyze these molecules. While searching PubChem for each compound's :blue[SMILES notation] (a machine-friendly 
representation) and other properties of choice is possible, it's time-consuming, and may often lead to errors.

To address this inefficiency, the :rainbow[ChemFetchTool] was developed. This freely available software simplifies the process of retrieving compound 
properties like SMILES, saving researchers valuable time.

The :rainbow[ChemFetchTool] offers two convenient ways to retrieve compound properties:

1. **:blue[Paste directly:]** Simply copy and paste the names of your molecules into the designated space in the sidebar.
2. **:blue[Upload a file:]** If you have a list of compound names in a CSV or TXT file, upload it in the designated space in the sidebar. 
You can then select the specific properties you'd like to retrieve.
Once you've provided your compounds and chosen the desired properties, click the "Retrieve" button to initiate the process.

""") 

st.divider()