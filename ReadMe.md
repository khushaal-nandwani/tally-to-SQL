## Tally To SQL

## Run
Under the `src` folder. Run `python main.py` in command line, and follow the instructions.

## Configuration
The program has been built to create SQL database in SQL Server. If you want to user another databse, please update the [database_.py](./src/database_.py) file.

## How will my database look like?
The tally exported XML has the following structure:
```xml
<ENVELOPE>
 <HEADER>
  <TALLYREQUEST>Import Data</TALLYREQUEST>
 </HEADER>
 <BODY>
  <IMPORTDATA>
   <REQUESTDESC>
    <REPORTNAME>All Masters</REPORTNAME>
    <STATICVARIABLES>
     <SVCURRENTCOMPANY>Khushaal Textiles</SVCURRENTCOMPANY>
    </STATICVARIABLES>
   </REQUESTDESC>
   <REQUESTDATA>
    <TALLYMESSAGE xmlns:UDF="TallyUDF">
        <GUID>1234</GUID>
        <VOUCHER>
            <!-- TAGS RELATED TO VOUCHER -->
        </VOUCHER>
    </TALLYMESSAGE>
    <TALLYMESSAGE xmlns:UDF="TallyUDF">
        <GUID>1235</GUID>
        <SOMEOTHERFIELD>
            <!-- TAGS RELATED TO SOMEOTTHERFIELD -->
             <ANOTHER.LIST>
                <NAME>SomeName</NAME>
                <GUID>1234</GUID>
             </ANOTHER.LIST>
        </SOMEOTTHERFIELD>
    </TALLYMESSAGE>
   </REQUESTDATA>
  </IMPORTDATA>
 </BODY>
</ENVELOPE>
```
Basically, everything useful comes under the TALLYMESSAGE tag. This includes, but is not limited to, VOUCHER, LEDGER, STOCKITEM, etc. 

This tool will create a table for each tag under the TALLYMESSAGE tag. 

If there is another nested tag under that tag, for example `ANOTHER.LIST` under the above example, it will create a table for that as well with the name `MASTANOTHERLIST`, with the GUID as the foreign key. The prefix `MAST` is added to the table name to diffrentiate master and transaction tables. You can change this prefix under (main.py)[./src/main.py]. 

I have chosen GUID as the foreign key because it is unique for each record and is present in all the tags.

### References Table
Since, every table under the nested tags will have a GUID as the foreign key, the program will create tables called `MASTTABLE_REFERENCES` and `TRANS_TABLE_REFERENCES`. These tables have two fields, the parent tag and the child tag or the nested tag which was created as a table. You can use this if you are confused where the GUID is coming from.