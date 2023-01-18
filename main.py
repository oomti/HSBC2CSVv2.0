import pdfplumber
import pandas
import locale
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('--input', required=True, help='Input file')
parser.add_argument('--output', required=True, help='Output file')

args = parser.parse_args()

# Now you can access the input, output, and verbose flags like this:
input_file = args.input
output_file = args.output

# Your code goes here

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


table_settings = {
    "vertical_strategy": "explicit",
    "horizontal_strategy": "text",
    "explicit_vertical_lines": [52,100,135,350,425, 515,550]
}
# Open the PDF file
with pdfplumber.open(input_file) as pdf:
  # Iterate through the pages of the PDF
  transaction_history = pandas.DataFrame(columns=["Transaction Date", "Transaction Type", "Transaction Details", "Paid Out", "Paid in", "Balance"])
  transaction_date = ""
  for page in pdf.pages:
    # Extract the lines and bounding boxes from the page
    left_position = 20
    right_position = 570
    topline_position = 0
    bottomline_position = 0
    try:
      topline_position = page.search("BALANCEBROUGHTFORWARD")[0]["top"]
      bottomline_position   = page.search("BALANCECARRIEDFORWARD")[0]["bottom"]
    except:
      print("THere is no balance on this page")
    else:
      page=page.crop((left_position,topline_position-20,right_position,bottomline_position))
      #im = page.to_image()
      #im.debug_tablefinder(table_settings).show()
      table = page.extract_table(table_settings)

      df = pandas.DataFrame(table,columns=["Transaction Date", "Transaction Type", "Transaction Details", "Paid Out", "Paid in", "Balance"])


      transaction_details = ""
      transaction_type = ""

      for index, row in df.iterrows():
      # check if the Amount column is not null
        transaction_details += " "+row["Transaction Details"]
        if ((row["Transaction Date"]!= "") & (row["Transaction Date"]!= "Date")):
          transaction_date = row["Transaction Date"]
        if (row["Transaction Type"] != ""):
          transaction_type = row["Transaction Type"]
        if (row["Paid in"]!="") or (row["Paid Out"]!="") or (row["Balance"]!=""):
        # store the value in the stored_amount variable
          row["Transaction Date"] = transaction_date
          row["Transaction Type"] = transaction_type
          row["Transaction Details"] = transaction_details
          temp_row = row

          transaction_details = ""
          transaction_type = ""
          df.loc[index] = temp_row

    
      
      
      

      # df["Transaction value"] = pandas.to_numeric(df["Paid in"],errors='coerce').fillna(0)-pandas.to_numeric(df["Paid Out"],errors='coerce').fillna(0)
        


      


      df.drop(df[(df["Paid Out"] == "") & (df["Paid in"] == "") & (df["Balance"] == "")].index,inplace = True)
      df=df.reset_index(drop=True)

      df.loc[:,"Balance"].iloc[-2]=df.loc[:,"Balance"].iloc[-1]
      try:
        paidin = locale.atof(df.loc[:,("Paid in")].iloc[2])
      except:
        paidin = 0

      try:
        paidout = locale.atof(df.loc[:,("Paid Out")].iloc[2])
      except:
        paidout = 0

      balance = locale.atof(df.loc[:,"Balance"].iloc[1])+paidin-paidout

      
      df.loc[:,"Balance"].iloc[2]='{:,.2f}'.format(balance)
      df.drop(df.index[0],axis=0,inplace = True)
      df.drop(df.index[0],axis=0,inplace = True)
      df.drop(df.index[-1],axis=0,inplace = True)

      transaction_history = pandas.concat([transaction_history,df])

      
transaction_history.to_csv(output_file,header=False,mode="a")   
    