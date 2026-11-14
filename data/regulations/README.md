
# Regulatory Corpus

## Purpose

This directory contains the official regulatory documents used by the
Environmental Clearance Pre-Screening Service.

The corpus supports regulatory document retrieval using LangChain
and ChromaDB.

## Primary Document

| Document | Description |
|---|---|
| EIA Notification 2006 - Original | Original notification S.O. 1533(E), dated 14 September 2006 |
| EIA Notification 2006 - Consolidated | Consolidated notification with amendments incorporated up to January 2026 |

## Directory Structure

- amendments/: Official Gazette amendments to the EIA Notification.
- office_memorandums/: Relevant official Office Memoranda and circulars.

## Document Metadata

Every document must be documented with:

- document_id
- document_name
- document_type
- issuing_authority
- document_number
- issue_date
- source_url
- retrieval_date
- applicability_status

## Important Retrieval Requirements

The RAG system must preserve:

1. Schedule entries and project categories.
2. Project thresholds and conditions.
3. General Conditions.
4. Relevant amendments.
5. Supporting Office Memoranda.

Schedule entries and General Conditions must remain independently
retrievable.

## Source and Version Control

Only official government documents are accepted as regulatory
evidence.

Original PDFs must not be modified.

The consolidated notification is used as a reference.
Where discrepancies occur, the applicable principal notification
and Gazette amendments must be checked.

Office Memoranda must be checked for applicability and status
before being used as current regulatory evidence.
