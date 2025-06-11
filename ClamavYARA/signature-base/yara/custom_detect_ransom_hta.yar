rule custom_detect_ransom_hta {
    meta:
        author = "cascade"
        description = "Detects the Simulation_rancongiciel.hta test file"
    strings:
        $s1 = "Votre système a été piraté" ascii wide nocase
        $s2 = "1000 BTC" ascii nocase
        $s3 = "ActiveXObject('WScript.Shell').Run" ascii
    condition:
        all of ($s*)
}
