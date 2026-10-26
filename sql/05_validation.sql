USE MedicineDB;
GO

SET NOCOUNT ON;

PRINT '========================================='
PRINT '1. TABLE EXISTENCE & ROW COUNTS'
PRINT '========================================='

SELECT 
    t.name AS [Table], 
    p.rows AS [Row_Count]
FROM sys.tables t
INNER JOIN sys.partitions p ON t.object_id = p.object_id
WHERE p.index_id IN (0, 1)
ORDER BY p.rows DESC;

PRINT '========================================='
PRINT '2. ORPHAN RECORD CHECKS (FOREIGN KEYS)'
PRINT '========================================='

-- Medicines -> Generics
DECLARE @med_gen_orphans INT;
SELECT @med_gen_orphans = COUNT(*) 
FROM dbo.medicines m
LEFT JOIN dbo.generics g ON m.generic_id = g.generic_id
WHERE g.generic_id IS NULL AND m.generic_id IS NOT NULL;
PRINT 'Orphan medicines (generic_id): ' + CAST(@med_gen_orphans AS VARCHAR);

-- Medicines -> Manufacturers
DECLARE @med_mfr_orphans INT;
SELECT @med_mfr_orphans = COUNT(*) 
FROM dbo.medicines m
LEFT JOIN dbo.manufacturers mf ON m.manufacturer_id = mf.manufacturer_id
WHERE mf.manufacturer_id IS NULL AND m.manufacturer_id IS NOT NULL;
PRINT 'Orphan medicines (manufacturer_id): ' + CAST(@med_mfr_orphans AS VARCHAR);

-- Medicines -> Dosage Forms
DECLARE @med_dos_orphans INT;
SELECT @med_dos_orphans = COUNT(*) 
FROM dbo.medicines m
LEFT JOIN dbo.dosage_forms df ON m.dosage_form_id = df.dosage_form_id
WHERE df.dosage_form_id IS NULL AND m.dosage_form_id IS NOT NULL;
PRINT 'Orphan medicines (dosage_form_id): ' + CAST(@med_dos_orphans AS VARCHAR);

-- Generics -> Drug Classes
DECLARE @gen_dcl_orphans INT;
SELECT @gen_dcl_orphans = COUNT(*) 
FROM dbo.generics g
LEFT JOIN dbo.drug_classes dc ON g.drug_class_id = dc.drug_class_id
WHERE dc.drug_class_id IS NULL AND g.drug_class_id IS NOT NULL;
PRINT 'Orphan generics (drug_class_id): ' + CAST(@gen_dcl_orphans AS VARCHAR);

-- Generics -> Indications
DECLARE @gen_ind_orphans INT;
SELECT @gen_ind_orphans = COUNT(*) 
FROM dbo.generics g
LEFT JOIN dbo.indications i ON g.indication_id = i.indication_id
WHERE i.indication_id IS NULL AND g.indication_id IS NOT NULL;
PRINT 'Orphan generics (indication_id): ' + CAST(@gen_ind_orphans AS VARCHAR);

PRINT '========================================='
PRINT '3. DATA QUALITY CHECKS'
PRINT '========================================='

DECLARE @invalid_prices INT;
SELECT @invalid_prices = COUNT(*) FROM dbo.medicines WHERE price < 0;
PRINT 'Medicines with negative price: ' + CAST(@invalid_prices AS VARCHAR);

DECLARE @invalid_packs INT;
SELECT @invalid_packs = COUNT(*) FROM dbo.medicines WHERE pack_size <= 0;
PRINT 'Medicines with pack_size <= 0: ' + CAST(@invalid_packs AS VARCHAR);

DECLARE @dup_classes INT;
SELECT @dup_classes = COUNT(*) FROM (
    SELECT drug_class_name FROM dbo.drug_classes GROUP BY drug_class_name HAVING COUNT(*) > 1
) sub;
PRINT 'Duplicate drug_class_name count (should be 0 after deduplication): ' + CAST(@dup_classes AS VARCHAR);

GO
