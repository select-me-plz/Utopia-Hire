export interface ResponseParser {
    certifications: string;
    education:      string;
    experience:     string;
    interests:      string;
    languages:      string;
    metadata:       Metadata;
    personal_info:  PersonalInfo;
    projects:       string;
    skills:         Skills;
}

export interface Metadata {
    all_detected_sections: string[];
    detected_language:     string;
    raw_text_length:       number;
    sample_text:           string;
}

export interface PersonalInfo {
    emails:   string[];
    language: string;
    name:     string;
    phones:   string[];
}

export interface Skills {
    extracted:    string[];
    full_section: string;
}