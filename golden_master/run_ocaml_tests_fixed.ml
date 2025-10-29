(* Golden Master Test Runner - OCaml Implementation (Fixed) *)
(* 
   Version simplifiée qui utilise uniquement les modules disponibles
   dans geneweb-oCaml
*)

(* Utiliser le module Geneweb_sosa directement *)
module Sosa = Geneweb_sosa

(* Helper to format Sosa operations *)
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

(* Helper pour les opérations Place - Version simplifiée *)
(* Note: Les fonctions Place ne sont pas dans l'API publique de geneweb *)
let run_place_operation op_data =
  let open Yojson.Basic.Util in
  let op = op_data |> member "op" |> to_string in
  `String ("Place operations not available in geneweb public API: " ^ op)

(* Helper pour les opérations Calendar - Non disponible *)
let run_calendar_operation op_data =
  let open Yojson.Basic.Util in
  let op = op_data |> member "op" |> to_string in
  `String ("Calendar operations not available in geneweb public API: " ^ op)

(* Process a single operation *)
let process_operation op_data test_type =
  match test_type with
  | "Sosa" -> run_sosa_operation op_data
  | "Place" -> run_place_operation op_data
  | "Calendar" -> run_calendar_operation op_data
  | _ -> `String ("Unknown test type: " ^ test_type)

(* Process a single test *)
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

(* Process a test file *)
let process_file input_file output_file =
  let json = Yojson.Basic.from_file input_file in
  let open Yojson.Basic.Util in
  
  let test_suite = json |> member "test_suite" |> to_string in
  let description = json |> member "description" |> to_string in
  let tests = json |> member "tests" |> to_list in
  
  (* Determine test type from suite name *)
  let test_type = 
    if String.contains test_suite 'S' || String.contains test_suite 's' then "Sosa"
    else if String.contains test_suite 'P' || String.contains test_suite 'p' then "Place"
    else if String.contains test_suite 'C' || String.contains test_suite 'c' then "Calendar"
    else "Unknown"
  in
  
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

(* Main function *)
let main () =
  let input_dir = "inputs" in
  let output_dir = "outputs_ocaml" in
  
  Printf.printf "🧪 Running OCaml Golden Master Tests\n";
  Printf.printf "📁 Input directory: %s\n" input_dir;
  Printf.printf "📁 Output directory: %s\n\n" output_dir;
  
  (* Create output directory if it doesn't exist *)
  (try Unix.mkdir output_dir 0o755 with Unix.Unix_error (Unix.EEXIST, _, _) -> ());
  
  (* Process each input file *)
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
