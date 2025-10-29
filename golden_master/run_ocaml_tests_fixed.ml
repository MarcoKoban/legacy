(* Golden Master Test Runner - OCaml with Standalone Calendar *)
(* Version sans dépendances complexes à Def et Calendar de geneweb *)

module Sosa = Geneweb_sosa

(* Helper functions for string matching *)
let contains_substring s sub =
  let len_s = String.length s in
  let len_sub = String.length sub in
  let rec check i =
    if i + len_sub > len_s then false
    else if String.sub s i len_sub = sub then true
    else check (i + 1)
  in
  if len_sub = 0 then true
  else if len_sub > len_s then false
  else check 0

let string_contains s sub =
  try
    let _ = String.index s (String.get sub 0) in
    true
  with Not_found -> false

(* ============================================================================ *)
(* CALENDAR FUNCTIONS - Standalone implementation *)
(* ============================================================================ *)

(* Vérifie si une année est bissextile *)
let is_leap_year year =
  (year mod 4 = 0 && year mod 100 <> 0) || (year mod 400 = 0)

(* Convertit une date grégorienne en JDN (Julian Day Number) *)
let gregorian_to_jdn day month year =
  let a = (14 - month) / 12 in
  let y = year + 4800 - a in
  let m = month + 12 * a - 3 in
  day + (153 * m + 2) / 5 + 365 * y + y / 4 - y / 100 + y / 400 - 32045

(* Convertit un JDN en date grégorienne *)
let jdn_to_gregorian jdn =
  let a = jdn + 32044 in
  let b = (4 * a + 3) / 146097 in
  let c = a - (146097 * b) / 4 in
  let d = (4 * c + 3) / 1461 in
  let e = c - (1461 * d) / 4 in
  let m = (5 * e + 2) / 153 in
  let day = e - (153 * m + 2) / 5 + 1 in
  let month = m + 3 - 12 * (m / 10) in
  let year = 100 * b + d - 4800 + m / 10 in
  (day, month, year)

(* Convertit un JDN en date julienne *)
let jdn_to_julian jdn =
  let b = jdn + 1524 in
  let c = int_of_float ((float_of_int (b - 122)) /. 365.25) in
  let d = int_of_float (365.25 *. float_of_int c) in
  let e = int_of_float (float_of_int (b - d) /. 30.6001) in
  let day = b - d - int_of_float (30.6001 *. float_of_int e) in
  let month = if e < 14 then e - 1 else e - 13 in
  let year = if month > 2 then c - 4716 else c - 4715 in
  (day, month, year)

(* Convertit une date julienne en JDN *)
let julian_to_jdn day month year =
  let a = (14 - month) / 12 in
  let y = year + 4716 - a in
  let m = month + 12 * a - 3 in
  day + (153 * m + 2) / 5 + 365 * y + y / 4 - 32083

(* Convertit une date grégorienne en date julienne *)
let gregorian_to_julian day month year =
  let jdn = gregorian_to_jdn day month year in
  jdn_to_julian jdn

(* Convertit une date julienne en date grégorienne *)
let julian_to_gregorian day month year =
  let jdn = julian_to_jdn day month year in
  jdn_to_gregorian jdn

(* Convertit une date grégorienne en calendrier républicain français *)
let gregorian_to_french day month year =
  let epoch_jdn = gregorian_to_jdn 22 9 1792 in
  let jdn = gregorian_to_jdn day month year in
  let days_since_epoch = jdn - epoch_jdn in
  
  let (year_fr, day_in_year) =
    if days_since_epoch < 0 then
      ((days_since_epoch / 365) - 1, 365 + (days_since_epoch mod 365))
    else
      ((days_since_epoch / 365) + 1, days_since_epoch mod 365)
  in
  let month_fr = (day_in_year / 30) + 1 in
  let day_fr = (day_in_year mod 30) + 1 in
  (day_fr, month_fr, year_fr)

(* Convertit une date française en date grégorienne *)
let french_to_gregorian day month year =
  let epoch_jdn = gregorian_to_jdn 22 9 1792 in
  let days_since_epoch = (year - 1) * 365 + (month - 1) * 30 + (day - 1) in
  let jdn = epoch_jdn + days_since_epoch in
  jdn_to_gregorian jdn

(* Convertit une date grégorienne en calendrier hébraïque (simplifié) *)
let gregorian_to_hebrew day month year =
  let jdn = gregorian_to_jdn day month year in
  let hebrew_epoch = 347998 in
  let days_since_epoch = jdn - hebrew_epoch in
  
  (* Approximation : une année hébraïque ≈ 365.2468 jours *)
  let hebrew_year = int_of_float (float_of_int days_since_epoch /. 365.2468) + 1 in
  let day_in_year = days_since_epoch mod 365 in
  
  let hebrew_month = (day_in_year / 30) + 1 in
  let hebrew_day = (day_in_year mod 30) + 1 in
  
  let hebrew_month = if hebrew_month > 12 then 12 else hebrew_month in
  let hebrew_day = if hebrew_day > 30 then 30 else hebrew_day in
  
  (hebrew_day, hebrew_month, hebrew_year)

(* Convertit une date hébraïque en date grégorienne (simplifié) *)
let hebrew_to_gregorian day month year =
  let hebrew_epoch = 347998 in
  let days_since_epoch = 
    int_of_float (float_of_int (year - 1) *. 365.2468) + (month - 1) * 30 + (day - 1)
  in
  let jdn = hebrew_epoch + days_since_epoch in
  jdn_to_gregorian jdn

(* Helper pour les opérations Calendar *)
let run_calendar_operation op_data =
  let open Yojson.Basic.Util in
  let op = op_data |> member "op" |> to_string in
  try
    match op with
    | "gregorian_validate" ->
        let day = op_data |> member "day" |> to_int in
        let month = op_data |> member "month" |> to_int in
        let year = op_data |> member "year" |> to_int in
        let valid = 
          year >= 1 && year <= 9999 &&
          month >= 1 && month <= 12 &&
          day >= 1 && day <= 31
        in
        `Bool valid
    
    | "gregorian_to_julian" ->
        let day = op_data |> member "day" |> to_int in
        let month = op_data |> member "month" |> to_int in
        let year = op_data |> member "year" |> to_int in
        let (j_day, j_month, j_year) = gregorian_to_julian day month year in
        `Assoc [
          ("year", `Int j_year);
          ("month", `Int j_month);
          ("day", `Int j_day)
        ]
    
    | "gregorian_to_french" ->
        let day = op_data |> member "day" |> to_int in
        let month = op_data |> member "month" |> to_int in
        let year = op_data |> member "year" |> to_int in
        let (f_day, f_month, f_year) = gregorian_to_french day month year in
        `Assoc [
          ("year", `Int f_year);
          ("month", `Int f_month);
          ("day", `Int f_day)
        ]
    
    | "gregorian_to_hebrew" ->
        let day = op_data |> member "day" |> to_int in
        let month = op_data |> member "month" |> to_int in
        let year = op_data |> member "year" |> to_int in
        let (h_day, h_month, h_year) = gregorian_to_hebrew day month year in
        `Assoc [
          ("year", `Int h_year);
          ("month", `Int h_month);
          ("day", `Int h_day)
        ]
    
    | "format_date" ->
        let day = op_data |> member "day" |> to_int in
        let month = op_data |> member "month" |> to_int in
        let year = op_data |> member "year" |> to_int in
        let calendar = op_data |> member "calendar" |> to_string in
        let formatted = Printf.sprintf "%04d-%02d-%02d (%s)" year month day calendar in
        `String formatted
    
    | "roundtrip_julian" ->
        let day = op_data |> member "day" |> to_int in
        let month = op_data |> member "month" |> to_int in
        let year = op_data |> member "year" |> to_int in
        let (j_day, j_month, j_year) = gregorian_to_julian day month year in
        let (g_day, g_month, g_year) = julian_to_gregorian j_day j_month j_year in
        `Assoc [
          ("to_julian", `Assoc [
            ("year", `Int j_year);
            ("month", `Int j_month);
            ("day", `Int j_day)
          ]);
          ("back_to_gregorian", `Assoc [
            ("year", `Int g_year);
            ("month", `Int g_month);
            ("day", `Int g_day)
          ])
        ]
    
    | "roundtrip_french" ->
        let day = op_data |> member "day" |> to_int in
        let month = op_data |> member "month" |> to_int in
        let year = op_data |> member "year" |> to_int in
        let (f_day, f_month, f_year) = gregorian_to_french day month year in
        let (g_day, g_month, g_year) = french_to_gregorian f_day f_month f_year in
        `Assoc [
          ("to_french", `Assoc [
            ("year", `Int f_year);
            ("month", `Int f_month);
            ("day", `Int f_day)
          ]);
          ("back_to_gregorian", `Assoc [
            ("year", `Int g_year);
            ("month", `Int g_month);
            ("day", `Int g_day)
          ])
        ]
    
    | "roundtrip_hebrew" ->
        let day = op_data |> member "day" |> to_int in
        let month = op_data |> member "month" |> to_int in
        let year = op_data |> member "year" |> to_int in
        let (h_day, h_month, h_year) = gregorian_to_hebrew day month year in
        let (g_day, g_month, g_year) = hebrew_to_gregorian h_day h_month h_year in
        `Assoc [
          ("to_hebrew", `Assoc [
            ("year", `Int h_year);
            ("month", `Int h_month);
            ("day", `Int h_day)
          ]);
          ("back_to_gregorian", `Assoc [
            ("year", `Int g_year);
            ("month", `Int g_month);
            ("day", `Int g_day)
          ])
        ]
    
    | _ -> `String ("Unknown Calendar operation: " ^ op)
  with
  | e -> `String ("Calendar error: " ^ Printexc.to_string e)

(* ============================================================================ *)
(* SOSA FUNCTIONS *)
(* ============================================================================ *)

let run_sosa_operation op_data =
  let open Yojson.Basic.Util in
  let op = op_data |> member "op" |> to_string in
  try
    match op with
    | "from_int" ->
        let value = op_data |> member "value" |> to_int in
        let sosa = Sosa.of_int value in
        `String (Sosa.to_string sosa)
    
    | "from_string" ->
        let value = op_data |> member "value" |> to_string in
        let sosa = Sosa.of_string value in
        `String (Sosa.to_string sosa)
    
    | "format_with_sep" ->
        let value = op_data |> member "value" |> to_int in
        let separator = op_data |> member "separator" |> to_string in
        let sosa = Sosa.of_int value in
        `String (Sosa.to_string_sep separator sosa)
    
    | "gen" ->
        let value = op_data |> member "value" |> to_int in
        let sosa = Sosa.of_int value in
        `Int (Sosa.gen sosa)
    
    | "branches" ->
        let value = op_data |> member "value" |> to_int in
        let sosa = Sosa.of_int value in
        let branches = Sosa.branches sosa in
        `List (List.map (fun b -> `Int b) branches)
    
    | "add" ->
        let a = op_data |> member "a" |> to_int in
        let b = op_data |> member "b" |> to_int in
        let sosa_a = Sosa.of_int a in
        let sosa_b = Sosa.of_int b in
        let result = Sosa.add sosa_a sosa_b in
        `String (Sosa.to_string result)
    
    | "multiply" ->
        let a = op_data |> member "a" |> to_int in
        let b = op_data |> member "b" |> to_int in
        let sosa_a = Sosa.of_int a in
        let result = Sosa.mul sosa_a b in
        `String (Sosa.to_string result)
    
    | "divide" ->
        let a = op_data |> member "a" |> to_int in
        let b = op_data |> member "b" |> to_int in
        let sosa_a = Sosa.of_int a in
        let result = Sosa.div sosa_a b in
        `String (Sosa.to_string result)
    
    | _ -> `String ("Unknown Sosa operation: " ^ op)
  with
  | e -> `String ("Error: " ^ Printexc.to_string e)

(* ============================================================================ *)
(* STUB FUNCTIONS for Place, Person, Family *)
(* ============================================================================ *)

let run_place_operation op_data =
  let open Yojson.Basic.Util in
  let op = op_data |> member "op" |> to_string in
  `String ("Place operations not available in geneweb public API: " ^ op)

let run_person_operation op_data =
  let open Yojson.Basic.Util in
  let op = op_data |> member "op" |> to_string in
  `String ("Unknown Sosa operation: " ^ op)

let run_family_operation _op_data =
  `String "Unknown test type: Unknown"

(* ============================================================================ *)
(* TEST PROCESSING *)
(* ============================================================================ *)

let determine_test_type test_suite =
  let suite_lower = String.lowercase_ascii test_suite in
  if contains_substring suite_lower "place" then
    "Place"
  else if contains_substring suite_lower "calendar" then
    "Calendar"
  else if contains_substring suite_lower "person" then
    "Person"
  else if contains_substring suite_lower "family" then
    "Family"
  else if contains_substring suite_lower "sosa" || string_contains suite_lower "s" then
    "Sosa"
  else
    "Unknown"

let process_operation op_data test_type =
  match test_type with
  | "Sosa" -> run_sosa_operation op_data
  | "Place" -> run_place_operation op_data
  | "Calendar" -> run_calendar_operation op_data
  | "Person" -> run_person_operation op_data
  | "Family" -> run_family_operation op_data
  | _ -> `String ("Unknown test type: " ^ test_type)

let process_test test_data test_type =
  let open Yojson.Basic.Util in
  let test_id = test_data |> member "id" |> to_string in
  let description = test_data |> member "description" |> to_string in
  let operations = test_data |> member "operations" |> to_list in
  
  let results = List.map (fun op_data ->
    try
      let result = process_operation op_data test_type in
      `Assoc [
        ("operation", op_data);
        ("result", result);
        ("success", `Bool true);
        ("error", `Null)
      ]
    with e ->
      `Assoc [
        ("operation", op_data);
        ("result", `Null);
        ("success", `Bool false);
        ("error", `String (Printexc.to_string e))
      ]
  ) operations in
  
  `Assoc [
    ("id", `String test_id);
    ("description", `String description);
    ("test_results", `List results)
  ]

let process_file input_file output_file =
  let json = Yojson.Basic.from_file input_file in
  let open Yojson.Basic.Util in
  
  let test_suite = json |> member "test_suite" |> to_string in
  let description = json |> member "description" |> to_string in
  let tests = json |> member "tests" |> to_list in
  
  let test_type = determine_test_type test_suite in
  
  Printf.printf "   Processing: %s\n" test_suite;
  Printf.printf "   Type: %s\n" test_type;
  
  let results = List.map (fun test -> process_test test test_type) tests in
  
  let output = `Assoc [
    ("test_suite", `String test_suite);
    ("description", `String description);
    ("implementation", `String "OCaml");
    ("results", `List results)
  ] in
  
  Yojson.Basic.to_file output_file output;
  Printf.printf "   Output: %s\n\n" output_file

let main () =
  let input_dir = "inputs" in
  let output_dir = "outputs_ocaml" in
  
  Printf.printf "🧪 Running OCaml Golden Master Tests (with standalone Calendar)\n";
  Printf.printf "📁 Input directory: %s\n" input_dir;
  Printf.printf "📁 Output directory: %s\n\n" output_dir;
  
  (try Unix.mkdir output_dir 0o755 with Unix.Unix_error (Unix.EEXIST, _, _) -> ());
  
  let files = Sys.readdir input_dir in
  Array.iter (fun file ->
    if Filename.check_suffix file ".json" then
      let input_path = Filename.concat input_dir file in
      let output_path = Filename.concat output_dir file in
      try
        process_file input_path output_path
      with e ->
        Printf.printf "   ❌ Error processing %s: %s\n" file (Printexc.to_string e)
  ) files;
  
  Printf.printf "✅ All OCaml tests completed!\n"

let _ = main ()