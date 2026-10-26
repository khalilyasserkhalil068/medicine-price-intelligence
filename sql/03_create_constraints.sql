USE MedicineDB;
GO

-- 1. Foreign Keys for Generics
ALTER TABLE dbo.generics
ADD CONSTRAINT FK_generics_drug_classes 
FOREIGN KEY (drug_class_id) REFERENCES dbo.drug_classes(drug_class_id);

ALTER TABLE dbo.generics
ADD CONSTRAINT FK_generics_indications 
FOREIGN KEY (indication_id) REFERENCES dbo.indications(indication_id);

-- 2. Foreign Keys for Medicines
ALTER TABLE dbo.medicines
ADD CONSTRAINT FK_medicines_generics 
FOREIGN KEY (generic_id) REFERENCES dbo.generics(generic_id);

ALTER TABLE dbo.medicines
ADD CONSTRAINT FK_medicines_manufacturers 
FOREIGN KEY (manufacturer_id) REFERENCES dbo.manufacturers(manufacturer_id);

ALTER TABLE dbo.medicines
ADD CONSTRAINT FK_medicines_dosage_forms 
FOREIGN KEY (dosage_form_id) REFERENCES dbo.dosage_forms(dosage_form_id);

-- 3. Indexes for Foreign Keys and common lookups
CREATE INDEX IX_generics_drug_class_id ON dbo.generics(drug_class_id);
CREATE INDEX IX_generics_indication_id ON dbo.generics(indication_id);

CREATE INDEX IX_medicines_generic_id ON dbo.medicines(generic_id);
CREATE INDEX IX_medicines_manufacturer_id ON dbo.medicines(manufacturer_id);
CREATE INDEX IX_medicines_dosage_form_id ON dbo.medicines(dosage_form_id);

GO
