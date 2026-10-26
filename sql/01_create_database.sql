USE master;
GO

IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'MedicineDB')
BEGIN
    CREATE DATABASE [MedicineDB];
END
GO
