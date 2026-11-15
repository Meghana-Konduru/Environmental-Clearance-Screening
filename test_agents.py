
from agents.screening_agent import run_screening_agent
from agents.regulatory_agent import run_regulatory_agent
from agents.risk_agent import run_risk_agent
from agents.report_agent import run_report_agent


def main():
    project_details = {
        "project_type": "Industrial project",
        "project_location": "Example industrial area, Karnataka",
        "proposed_activity": "Manufacturing facility",
        "project_capacity": "Not yet specified",
        "water_usage": "Groundwater extraction",
        "waste_generation": "Industrial wastewater",
    }

    print("\n1. RUNNING SCREENING AGENT")
    screening_result = run_screening_agent(project_details)
    print("Screening completed.")

    print("\n2. RUNNING REGULATORY AGENT")
    regulatory_result = run_regulatory_agent(project_details)
    regulatory_context = regulatory_result["regulatory_context"]
    print(f"Retrieved {len(regulatory_context)} regulatory passages.")

    print("\n3. RUNNING RISK AGENT")
    risk_result = run_risk_agent(project_details)
    print("Risk review completed.")

    print("\n4. RUNNING REPORT AGENT")
    final_report = run_report_agent(
        project_details=project_details,
        screening_result=screening_result,
        regulatory_context=regulatory_context,
        risk_assessment=risk_result,
    )
    print("Final report generated.")

    print("\nWORKFLOW SUMMARY")
    print("=" * 45)
    print("Screening:", bool(screening_result))
    print("Regulatory passages:", len(regulatory_context))
    print("Risk assessment:", bool(risk_result))
    print("Final report:", bool(final_report))
    print("Report title:", final_report.get("report_title"))
    print("\nAll four agent interfaces executed successfully.")


if __name__ == "__main__":
    main()
