# COVID Consultant for Hex Cambridge

## What does the Program do
The application aims to give you a general idea about the specific risk levels of various areas in your locality, to assess the relative risk of traveling to or through a specified location and recommend the best route. It gathers data from live information on government websites, live news updates and live footage (from CCTV cameras, for example), to make accurate, bespoke recommendations, which can advise travel. The information is presented in the form of interactive maps, news bulletins and a chatbot interface for general queries.


 ## How did we design it
 For the heatmap, we used google maps API to extract geographical data used to plot the course between two points for various modes of travel. We combined it with the geographical data for COVID statistics extracted from government websites, applying our custom algorithm to it to generate a heat map based on risk. We also trained convolutional neural networks on CCTV footage to detect approximate density of people in an area (such as a mall or a park) and also other specific insights such as the proportion of people with masks on, and the overall level of effective social distancing. The dashboard also contains live updates from local news outlets, which are curated for the user. Additionally, a deep learning-based chatbot has been integrated that offers general advice and guidance.

