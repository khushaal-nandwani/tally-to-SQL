<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:UDF="TallyUDF">
    <!-- Identity transform -->
    <xsl:template match="@*|node()">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>

    <!-- Special template for TALLYMESSAGE to include GUID attribute -->
    <xsl:template match="TALLYMESSAGE">
        <xsl:copy>
            <xsl:apply-templates select="@*"/>
            <!-- Add GUID attribute by searching for the first GUID element anywhere within TALLYMESSAGE -->
            <xsl:attribute name="GUID">
                <xsl:value-of select=".//GUID[1]"/>
            </xsl:attribute>
            <xsl:apply-templates select="node()"/>
        </xsl:copy>
    </xsl:template>
</xsl:stylesheet>