USE MedicineDB;
GO

-- 1. Manufacturers
CREATE TABLE dbo.manufacturers (
    manufacturer_id INT NOT NULL,
    manufacturer_name NVARCHAR(255) NOT NULL,
    slug NVARCHAR(255) NULL,
    generics_count INT NULL CHECK (generics_count >= 0),
    brand_names_count INT NULL CHECK (brand_names_count >= 0),
    CONSTRAINT PK_manufacturers PRIMARY KEY (manufacturer_id),
    CONSTRAINT UQ_manufacturer_name UNIQUE (manufacturer_name)
);

-- 2. Dosage Forms
CREATE TABLE dbo.dosage_forms (
    dosage_form_id INT NOT NULL,
    dosage_form_name NVARCHAR(255) NOT NULL,
    slug NVARCHAR(255) NULL,
    brand_names_count INT NULL CHECK (brand_names_count >= 0),
    CONSTRAINT PK_dosage_forms PRIMARY KEY (dosage_form_id),
    CONSTRAINT UQ_dosage_form_name UNIQUE (dosage_form_name)
);

-- 3. Drug Classes
-- Expected deduplicated to canonical IDs
CREATE TABLE dbo.drug_classes (
    drug_class_id INT NOT NULL,
    drug_class_name NVARCHAR(255) NOT NULL,
    slug NVARCHAR(255) NULL,
    generics_count INT NULL CHECK (generics_count >= 0),
    CONSTRAINT PK_drug_classes PRIMARY KEY (drug_class_id),
    CONSTRAINT UQ_drug_class_name UNIQUE (drug_class_name)
);

-- 4. Indications
CREATE TABLE dbo.indications (
    indication_id INT NOT NULL,
    indication_name NVARCHAR(500) NOT NULL,
    slug NVARCHAR(255) NULL,
    generics_count INT NULL CHECK (generics_count >= 0),
    CONSTRAINT PK_indications PRIMARY KEY (indication_id),
    CONSTRAINT UQ_indication_name UNIQUE (indication_name)
);

-- 5. Generics
CREATE TABLE dbo.generics (
    generic_id INT NOT NULL,
    generic_name NVARCHAR(500) NOT NULL,
    slug NVARCHAR(255) NULL,
    monograph_link NVARCHAR(MAX) NULL,
    drug_class_id INT NULL,
    indication_id INT NULL,
    indication_description_clean NVARCHAR(MAX) NULL,
    therapeutic_class_description_clean NVARCHAR(MAX) NULL,
    pharmacology_description_clean NVARCHAR(MAX) NULL,
    dosage_description_clean NVARCHAR(MAX) NULL,
    administration_description_clean NVARCHAR(MAX) NULL,
    interaction_description_clean NVARCHAR(MAX) NULL,
    contraindications_description_clean NVARCHAR(MAX) NULL,
    side_effects_description_clean NVARCHAR(MAX) NULL,
    pregnancy_and_lactation_description_clean NVARCHAR(MAX) NULL,
    precautions_description_clean NVARCHAR(MAX) NULL,
    pediatric_usage_description_clean NVARCHAR(MAX) NULL,
    overdose_effects_description_clean NVARCHAR(MAX) NULL,
    duration_of_treatment_description_clean NVARCHAR(MAX) NULL,
    reconstitution_description_clean NVARCHAR(MAX) NULL,
    storage_conditions_description_clean NVARCHAR(MAX) NULL,
    CONSTRAINT PK_generics PRIMARY KEY (generic_id),
    CONSTRAINT UQ_generic_name UNIQUE (generic_name)
);

-- 6. Medicines
CREATE TABLE dbo.medicines (
    brand_id INT NOT NULL,
    brand_name NVARCHAR(255) NOT NULL,
    type NVARCHAR(50) NOT NULL CHECK (type IN ('allopathic', 'herbal')),
    slug NVARCHAR(255) NULL,
    generic_id INT NULL,
    manufacturer_id INT NOT NULL,
    dosage_form_id INT NOT NULL,
    strength NVARCHAR(255) NULL,
    strength_normalized NVARCHAR(255) NULL,
    package_description NVARCHAR(MAX) NULL,
    price DECIMAL(18,2) NULL CHECK (price >= 0),
    pack_price DECIMAL(18,2) NULL CHECK (pack_price >= 0),
    pack_size DECIMAL(18,2) NULL CHECK (pack_size > 0),
    currency NVARCHAR(10) NOT NULL DEFAULT 'BDT',
    CONSTRAINT PK_medicines PRIMARY KEY (brand_id)
);
GO
