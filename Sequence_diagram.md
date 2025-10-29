```mermaid
sequenceDiagram
    participant User
    participant WebServer
    participant Config
    participant Templates
    participant Database
    participant Display
    participant Output

    User->>WebServer: HTTP Request (genealogy page)
    WebServer->>Config: Parse request parameters
    Config->>Config: Determine operation mode (m=)
    
    alt Person Display (m=P)
        Config->>Database: Load person data (Driver.poi)
        Database-->>Config: Person record
        Config->>Templates: Select template (perso.txt)
        Templates->>Display: Generate person view
        Display->>Output: Render HTML
    
    else Descendants Display (m=D)
        Config->>Database: Load person + descendants
        Database-->>Config: Family tree data
        alt Tree View (t=T)
            Config->>Templates: Use destree.txt template
        else Table View (t=H)
            Config->>Display: Call descendDisplay.ml
            Display->>Output: Generate table
        else List View (t=L)
            Config->>Templates: Use deslist template
        end
    
    else Ancestors Display (m=A)
        Config->>Database: Load ancestors data
        Database-->>Config: Ancestor records
        alt Sosa Table (t=S)
            Config->>Templates: Use ancsosa_tab.txt
        else Tree View (t=T)
            Config->>Templates: Use anctree.txt
        else Fan Chart (t=FC)
            Config->>Templates: Use fanchart.txt
        end
    
    else Relationship (m=R)
        Config->>Database: Load relationship path
        Database-->>Config: Relationship data
        Config->>Display: Call relationDisplay.ml
        Display->>Output: Generate relationship diagram
    
    else Edit Mode (m=MOD_IND)
        Config->>Database: Load person for editing
        Database-->>Config: Editable person data
        Config->>Templates: Use updind.txt template
        Templates->>Output: Generate edit form
        User->>WebServer: Submit changes
        WebServer->>Database: Update person record
    
    else Merge Operation (m=MRG_IND)
        Config->>Database: Load persons to merge
        Database-->>Config: Person records
        Config->>Display: Call mergeIndDisplay.ml
        Display->>Output: Generate merge interface
    
    else Calendar View (m=CAL)
        Config->>Database: Load birth/death dates
        Database-->>Config: Date records
        Config->>Templates: Use calendar.txt
        Templates->>Output: Generate calendar
    
    else Gallery View (m=NOTES with gallery)
        Config->>Database: Load image metadata
        Database-->>Config: Image records
        Config->>Templates: Use notes_gallery.txt
        Templates->>Output: Generate image gallery
    end
    
    Output->>WebServer: Complete HTML response
    WebServer->>User: HTTP Response (rendered page)
    
    Note over Database: Data stored in .gwb format<br/>Accessed via Driver module
    Note over Templates: Template files in hd/etc/<br/>Use special syntax for data binding
    Note over Display: ML modules handle complex<br/>rendering logic (tables, trees, etc.)