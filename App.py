import streamlit as st
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import pandas as pd
from collections import defaultdict as dd
from PubChemAPI import getPropertiesFromPubchem

########################################################################################################################################################
#                                                                       Page Setup                                                                     #
########################################################################################################################################################

st.set_page_config(
    page_title="ChemFetchTool",
    page_icon="favicon.png",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={'About': "Retrieve molecular properties of a molecule"})

########################################################################################################################################################
#                                                                       Functions                                                                      #
########################################################################################################################################################

@st.cache_data(show_spinner=False)
def retrieveProperties(df, mol_col, properties):
  # with st.spinner("##### :rainbow[ChemFetchTool] is retrieving the selected properties. You may take a walk. Results will be ready soon ⏳"):
  total_items = len(df)
  completed_items = 0
  my_progress_bar = st.progress(0)

  no_of_properties = len(properties)
  if total_items == 1:
    if no_of_properties == 1:
      progress_text = f":rainbow[ChemFetchTool] is retrieving {no_of_properties} selected property for {total_items} compound"
    else:
      progress_text = f":rainbow[ChemFetchTool] is retrieving {no_of_properties} selected properties for {total_items} compound"
  else:
    if no_of_properties == 1:
      progress_text = f":rainbow[ChemFetchTool] is retrieving {no_of_properties} selected property for {total_items} compounds"
    else:
      progress_text = f":rainbow[ChemFetchTool] is retrieving {no_of_properties} selected properties for {total_items} compounds"

  status_text = st.empty()
  status_text.write(f"##### {progress_text}. 0 set retrieved ⟶ 0% complete")

  retrieved_properties = dd(list)

  for name in df[mol_col]:
    retrieved_properties[mol_col].append(name)
    for prop in properties:
      retrieved_properties[prop].append(getPropertiesFromPubchem(name, prop))
    completed_items += 1
    progress = int((completed_items/total_items)*100)
    my_progress_bar.progress(progress)
    if completed_items == 1:
      status_text.write(f"##### {progress_text}. {completed_items} set retrieved ⟶ {progress}% complete")
    else:
      status_text.write(f"##### {progress_text}. {completed_items} sets retrieved ⟶ {progress}% complete")

  if total_items == 1:
    if no_of_properties == 1:
      status_text.success(f"#### :orange[Operation complete! {no_of_properties} selected property of {completed_items} compound successfully retrieved]")
    else:
      status_text.success(f"#### :orange[Operation complete! {no_of_properties} selected properties of {completed_items} compound successfully retrieved]")
  else:
    if no_of_properties == 1:
      status_text.success(f"#### :orange[Operation complete! {no_of_properties} selected property of {completed_items} compounds successfully retrieved]")
    else:
      status_text.success(f"#### :orange[Operation complete! {no_of_properties} selected properties of {completed_items} compounds successfully retrieved]")

  my_progress_bar.empty()
  retrieved_properties_df = pd.DataFrame(retrieved_properties)
  return retrieved_properties_df

def addSNoAsIndex(df):
    df_len = len(df)
    df["S/No"] = range(1, df_len+1)
    df = df.set_index("S/No")
    return df

@st.cache_data
def convert_df(df):
    return df.to_csv().encode('utf-8')

########################################################################################################################################################
#                                                                     page  division                                                                   #
########################################################################################################################################################

col_a, col_b = st.columns([3, 1.7], gap="large")

########################################################################################################################################################
#                                                                     right column                                                                     #
########################################################################################################################################################

uploaded_file_df = None
uploaded_names = None

with col_b:
  st.write("##### :blue[Paste your compound names here] :red[(Must be one per line)]")
  col_b1, col_b2 = st.columns([4.5, 1.5])
  with col_b1:
    if "uploaded_names" not in st.session_state:
      st.session_state["uploaded_names"] = None
    # st.write("##### :blue[Paste your compound names here] :red[(Must be one per line)]")
    uploaded_names = st.text_area("Paste your compound names here", value=None, height=105, max_chars=None, label_visibility="collapsed",
                                  placeholder="E.g.\nQuercetin\nGlucuronic Acid\n(+)-Catechin 5-gallate", key="text")
    if uploaded_names:
      st.session_state["uploaded_names"] = uploaded_names

  def clearTextArea():
    st.session_state.text = None

  with col_b2:
    refresh_button = st.button("**:white[Clear Names]**", type="secondary", on_click=clearTextArea, help="Clears the text area when clicked")

  if "uploaded_file" not in st.session_state:
    st.session_state["uploaded_file"] = None
  st.write("##### :blue[Or Choose a file] :red[(Must be a CSV or TXT file)]")
  uploaded_file = st.file_uploader("Or Choose a file", type=['csv', 'txt'], label_visibility="collapsed")
  if uploaded_file:
    st.session_state["uploaded_file"] = uploaded_file

  if uploaded_file is not None:
    uploaded_file_df = pd.read_csv(uploaded_file)
    col_names = uploaded_file_df.columns.tolist()
    st.write("##### :blue[Select Column with molecule names]")
    mol_names = st.radio("Select Column with molecule names", col_names, index=None, horizontal=True, label_visibility="collapsed")
  
  st.write("##### :blue[Check the properties to be retrieved]")
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

  st.divider()
  col1, col2, col3 = st.columns([1, 1, 1])
  button = col2.button("**:white[Submit Job]**", type="primary", help="Submits the requested job to initiate the retrieval process when clicked")

  st.divider()

########################################################################################################################################################
#                                                                     left column                                                                      #
########################################################################################################################################################

with col_a:
  # Design 1
  st.write("## :rainbow[ChemFetchTool: Automate Molecular Properties Retrieval from PubChem]")
  st.divider()
  cola1, cola2 = st.columns([0.4, 0.6], gap="large")
  cola2.image("favicon.png", width=None, use_column_width="auto")
  cola2.subheader(":rainbow[From molecule names to properties]")
  
  # Design 2
  # col11, col22 = st.columns([0.5, 0.5], gap="large")
  # with col11:
  #   st.divider()
  #   st.title(":rainbow[ChemFetchTool]")
  #   st.divider()
  # with col22:
  #   st.image("favicon.png", width=None, use_column_width="auto")
  #   st.subheader(":rainbow[From molecule names to properties]")

  st.divider()

  help_text = "Click to download results"
  
  if button:
    try:
      if uploaded_file_df is not None and uploaded_names is not None:
        st.warning("##### Both molecule name(s) and file Provided. Clear text area or remove file but NOT both")
      
      elif uploaded_file_df is None and uploaded_names is None:
        st.warning("##### No names or file Provided! Paste molecules names or submit a molecule file but NOT both")

      elif uploaded_names is not None:
        if properties:
          uploaded_names =  uploaded_names.strip(" ,:;.''").split("\n")
          uploaded_names_df = pd.DataFrame(uploaded_names, columns=["Compound"])
          retrieved_properties_df = retrieveProperties(uploaded_names_df, "Compound", properties)
          retrieved_properties_df = addSNoAsIndex(retrieved_properties_df)

          csv = convert_df(retrieved_properties_df)
          st.download_button(label="Download Properties as CSV", data=csv, file_name='Retrieved_properties_df.csv', mime='text/csv', type="primary", 
                             help=help_text)

          st.write(retrieved_properties_df)
        else:
          st.warning("##### At least one properties must be selected")

      elif uploaded_file_df is not None:
        if mol_names is not None and properties:
          retrieved_properties_df = retrieveProperties(uploaded_file_df, mol_names, properties)
          retrieved_properties_df = addSNoAsIndex(retrieved_properties_df)

          csv = convert_df(retrieved_properties_df)
          st.download_button(label="Download Properties as CSV", data=csv, file_name='Retrieved_properties_df.csv', mime='text/csv', type="primary", 
                             help=help_text)

          st.write(retrieved_properties_df)
        else:
          st.warning("##### The column with molecule names and at least one properties must be selected")
    except (requests.RequestException, ConnectionError):
      st.warning("##### Connection error occured. Ensure a stable network connection and resubmit Job!")
    except:
      st.warning("##### An unknown error occured. Ensure a stable network connection and resubmit Job!")

    st.divider()

  # else:
  st.write("""
  Scientific articles often list compounds with interesting pharmacological effects, but only by name. This poses a problem for researchers who 
  need a computer-readable format to analyze these molecules. While searching PubChem for each compound's **:blue[SMILES notation]** (a machine-friendly 
  representation) and other properties of choice is possible, it's time-consuming, and may often lead to errors. To address this inefficiency, the 
  **:rainbow[ChemFetchTool]** was developed. This freely available software simplifies the process of retrieving compound properties like SMILES, saving 
  researchers valuable time.

  The **:rainbow[ChemFetchTool]** offers two convenient ways to retrieve compound properties:

  1. **:blue[Paste directly:]** Simply copy and paste the names of your molecules into the designated space in the sidebar.
  2. **:blue[Upload a file:]** If you have a list of compound names in a CSV or TXT file, upload it in the designated space in the sidebar. 
  """) 
  st.write("""
  You can then select the specific properties you'd like to retrieve. Once you've provided your compounds and chosen the desired properties, 
  click the **:red[|Submit Job|]** button to initiate the process.
  """)

  st.divider()

with st.container():
    st.markdown("""       
    #### Further information:  
                
     **References**:      
     Kim S, Thiessen PA, Bolton EE. Programmatic Retrieval of Small Molecule Information from PubChem Using PUG-REST. In Kutchukian PS, 
     ed. Chemical Biology Informatics and Modeling. Methods in Pharmacology and Toxicology. New York, NY: Humana Press, 2018, pp. 1-24. 
     [[Full Text]](https://link.springer.com/protocol/10.1007/7653_2018_30).
    
     * The authors have published a number of works in the _in silico_ drug design/bioinformatics and chemoinformatics domains spanning across
       various disease conditions like `Cancer`, `Infectious Diseases`, and `Neurodegenerative Disorders`. Notable examples
       include:  
        * Ibezim A, **Onah E**, Osigwe SC, Okoroafor PU, Ukoha OP, De Siqueira-Neto JL, Ntie-Kang F and Ramanathan, K. Potential 
          Dual Inhibitors of Hexokinases and Mitochondrial Complex I Discovered Through Machine Learning Approach. Available at SSRN:  
          [https://dx.doi.org/10.2139/ssrn.4635544](https://dx.doi.org/10.2139/ssrn.4635544)
        * **Onah E**, Uzor PF, Ugwoke IC, Eze JU, Ugwuanyi ST, Chukwudi IR, Ibezim A. Prediction of HIV-1 protease cleavage site 
          from octapeptide sequence information using selected classifiers and hybrid descriptors. BMC Bioinformatics. 2022 Nov 
          8;23(1):466. PMID: 36344934. PMCID: 9641908.  
          [https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9641908/](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9641908/). 
        * Ibezim A, **Onah E**, Dim EN, Ntie-Kang F. A computational multi-targeting approach for drug repositioning for psoriasis 
          treatment. BMC Complement Med Ther. 2021 Jul 5;21(1):193. PMID: 34225727. PMCID: 8258956.  
          [https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8258956/](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8258956/).
        * **Onah, E**., Ugwoke, I., Eze, U., Eze, H., Musa, S., Ndiana-Abasi, S., Okoli, O., Ekeh, I., & Edet, A. (2021). 
          Search for Structural Scaffolds Against SARS-COV-2 Mpro: An In Silico Study. Journal of Fundamental and Applied 
          Sciences, 13(2), 740-769.   
          [https://jfas.info/index.php/JFAS/article/view/987](https://jfas.info/index.php/JFAS/article/view/987).
          """)
    st.markdown("""#### If you make use of **:rainbow[ChemFetchTool]** in your work, please cite it as follows:  
    Onah, E. (2024). ChemFetchTool: Automate Molecular Properties Retrieval from PubChem (Version 1.1.0) Zenodo. https://doi.org/10.5281/zenodo.10850870.""")