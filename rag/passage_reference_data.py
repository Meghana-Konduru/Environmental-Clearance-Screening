
"""
Manually labelled reference passages for RAG evaluation.

These references are based on the passage inspection output.
They are initial relevance labels, not legal validation.

The source documents and provisions must be checked against
authoritative current versions before legal use.
"""

PASSAGE_REFERENCE_CASES = [
    {
        "scenario": "Public hearing",
        "query": (
            "What is the procedure, notice period and responsibility "
            "for conducting an environmental public hearing?"
        ),
        "references": [
            {
                "source": "eia_notification_2006_consolidated.pdf",
                "page": 9,
                "excerpt": (
                    "the public hearing at, or in close proximity to, "
                    "the site(s) in all cases shall be conducted by the "
                    "State Pollution Control Board (SPCB) or the Union "
                    "Territory Pollution Control Committee (UTPCC)"
                ),
            },
            {
                "source": "eia_notification_2006_consolidated.pdf",
                "page": 50,
                "excerpt": (
                    "the public hearing proceedings to the concerned "
                    "regulatory authority within 8 (eight) days of the "
                    "completion of the public hearing"
                ),
            },
            {
                "source": "SO_3067_E_2009.pdf",
                "page": 29,
                "excerpt": (
                    "If the SPCB or UTPCC fails to hold the public "
                    "hearing within the stipulated 45 (forty five) days"
                ),
            },
        ],
    },
    {
        "scenario": "Mining",
        "query": (
            "What environmental clearance requirements, Schedule "
            "entries and thresholds apply to mining projects?"
        ),
        "references": [
            {
                "source": "eia_notification_2006_consolidated.pdf",
                "page": 18,
                "excerpt": (
                    "Mining, extraction of natural resources and "
                    "power generation"
                ),
            },
            {
                "source": "eia_notification_2006_consolidated.pdf",
                "page": 6,
                "excerpt": (
                    "in Form 1M for mining of minor minerals up to "
                    "five hectare under Category ‘B2’ projects"
                ),
            },
        ],
    },
    {
        "scenario": "Projects near protected areas",
        "query": (
            "What regulatory procedures apply to projects located "
            "near national parks, wildlife sanctuaries and protected areas?"
        ),
        "references": [
            {
                "source": "OM_2020-07-16_NBWL_clearance_procedure.pdf",
                "page": 1,
                "excerpt": (
                    "prior clearance from the Standing Committee of "
                    "the National Board of Wild Life will be required"
                ),
            },
            {
                "source": "OM_2019-08-08_projects_within_10km_protected_areas.pdf",
                "page": 2,
                "excerpt": (
                    "Proposals involving developmental activity/project "
                    "located within 10 km of National Park/Wildlife "
                    "Sanctuary wherein final ESZ notification is not "
                    "notified"
                ),
            },
            {
                "source": "eia_notification_2006_consolidated.pdf",
                "page": 39,
                "excerpt": (
                    "The project to be located within 10 km of the "
                    "National Parks, Sanctuaries, Biosphere Reserves, "
                    "Migratory Corridors of Wild Animals"
                ),
            },
        ],
    },
    {
        "scenario": "Projects involving forest land",
        "query": (
            "What procedures apply when a project involves forest "
            "land diversion and wildlife habitat?"
        ),
        "references": [
            {
                "source": "OM_2009-12-02_forest_wildlife_procedure.pdf",
                "page": 1,
                "excerpt": (
                    "the application for diversion of forestland has "
                    "been submitted by the project proponent before "
                    "they come for environment clearance"
                ),
            },
            {
                "source": "OM_2009-12-02_forest_wildlife_procedure.pdf",
                "page": 1,
                "excerpt": (
                    "The project proponent should submit their "
                    "application for wildlife Clearance"
                ),
            },
        ],
    },
]
