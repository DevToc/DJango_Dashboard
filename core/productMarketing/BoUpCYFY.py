

def BoUpCy(dfAllBoUp):
    adj_boup = dfAllBoUp.drop(['fy_vol2020', 'fy_vol2021', 'fy_vol2022', 'fy_vol2023', 'fy_vol2024', 'fy_vol2025', 'fy_vol2026', 'fy_vol2027', 'fy_vol2028', 'fy_vol2029', 'fy_vol2030', 'fy_vol2031', 'fy_vol2032', 'fy_vol2033', 'fy_vol2034', 'fy_vol2035', 'fy_vol2036', 'fy_vol2037', 'fy_vol2038', 'fy_vol2039', 'fy_vol2040', 'fy_vol2041', 'fy_vol2042', 'fy_vol2043', 'fy_vol2044',
                               'fy_gm2020', 'fy_gm2021', 'fy_gm2022', 'fy_gm2023', 'fy_gm2024', 'fy_gm2025', 'fy_gm2026', 'fy_gm2027', 'fy_gm2028', 'fy_gm2029', 'fy_gm2030', 'fy_gm2031', 'fy_gm2032', 'fy_gm2033', 'fy_gm2034', 'fy_gm2035', 'fy_gm2036', 'fy_gm2037', 'fy_gm2038', 'fy_gm2039', 'fy_gm2040', 'fy_gm2041', 'fy_gm2042', 'fy_gm2043', 'fy_gm2044',
                               'fy_wVol2020', 'fy_wVol2021', 'fy_wVol2022', 'fy_wVol2023', 'fy_wVol2024', 'fy_wVol2025', 'fy_wVol2026', 'fy_wVol2027', 'fy_wVol2028', 'fy_wVol2029', 'fy_wVol2030', 'fy_wVol2031', 'fy_wVol2032', 'fy_wVol2033', 'fy_wVol2034', 'fy_wVol2035', 'fy_wVol2036', 'fy_wVol2037', 'fy_wVol2038', 'fy_wVol2039', 'fy_wVol2040', 'fy_wVol2041', 'fy_wVol2042', 'fy_wVol2043', 'fy_wVol2044',
                               'fy_wRev2020', 'fy_wRev2021', 'fy_wRev2022', 'fy_wRev2023', 'fy_wRev2024', 'fy_wRev2025', 'fy_wRev2026', 'fy_wRev2027', 'fy_wRev2028', 'fy_wRev2029', 'fy_wRev2030', 'fy_wRev2031', 'fy_wRev2032', 'fy_wRev2033', 'fy_wRev2034', 'fy_wRev2035', 'fy_wRev2036', 'fy_wRev2037', 'fy_wRev2038', 'fy_wRev2039', 'fy_wRev2040', 'fy_wRev2041', 'fy_wRev2042', 'fy_wRev2043', 'fy_wRev2044'], axis=1)
    boupCY = adj_boup.rename(columns={
        'vol2020': 'CY_vol2020',
        'vol2021': 'CY_vol2021',
        'vol2022': 'CY_vol2022',
        'vol2023': 'CY_vol2023',
        'vol2024': 'CY_vol2024',
        'vol2025': 'CY_vol2025',
        'vol2026': 'CY_vol2026',
        'vol2027': 'CY_vol2027',
        'vol2028': 'CY_vol2028',
        'vol2029': 'CY_vol2029',
        'vol2030': 'CY_vol2030',
        'vol2031': 'CY_vol2031',
        'vol2032': 'CY_vol2032',
        'vol2033': 'CY_vol2033',
        'vol2034': 'CY_vol2034',
        'vol2035': 'CY_vol2035',
        'vol2036': 'CY_vol2036',
        'vol2037': 'CY_vol2037',
        'vol2038': 'CY_vol2038',
        'vol2039': 'CY_vol2039',
        'vol2040': 'CY_vol2040',
        'vol2041': 'CY_vol2041',
        'vol2042': 'CY_vol2042',
        'vol2043': 'CY_vol2043',
        'vol2044': 'CY_vol2044',

        'volCustomer2020': 'CY_volCustomer2020',
        'volCustomer2021': 'CY_volCustomer2021',
        'volCustomer2022': 'CY_volCustomer2022',
        'volCustomer2023': 'CY_volCustomer2023',
        'volCustomer2024': 'CY_volCustomer2024',
        'volCustomer2025': 'CY_volCustomer2025',
        'volCustomer2026': 'CY_volCustomer2026',
        'volCustomer2027': 'CY_volCustomer2027',
        'volCustomer2028': 'CY_volCustomer2028',
        'volCustomer2029': 'CY_volCustomer2029',
        'volCustomer2030': 'CY_volCustomer2030',
        'volCustomer2031': 'CY_volCustomer2031',
        'volCustomer2032': 'CY_volCustomer2032',
        'volCustomer2033': 'CY_volCustomer2033',
        'volCustomer2034': 'CY_volCustomer2034',
        'volCustomer2035': 'CY_volCustomer2035',
        'volCustomer2036': 'CY_volCustomer2036',
        'volCustomer2037': 'CY_volCustomer2037',
        'volCustomer2038': 'CY_volCustomer2038',
        'volCustomer2039': 'CY_volCustomer2039',
        'volCustomer2040': 'CY_volCustomer2040',
        'volCustomer2041': 'CY_volCustomer2041',
        'volCustomer2042': 'CY_volCustomer2042',
        'volCustomer2043': 'CY_volCustomer2043',
        'volCustomer2044': 'CY_volCustomer2044',

        'price2020': 'CY_price2020',
        'price2021': 'CY_price2021',
        'price2022': 'CY_price2022',
        'price2023': 'CY_price2023',
        'price2024': 'CY_price2024',
        'price2025': 'CY_price2025',
        'price2026': 'CY_price2026',
        'price2027': 'CY_price2027',
        'price2028': 'CY_price2028',
        'price2029': 'CY_price2029',
        'price2030': 'CY_price2030',
        'price2031': 'CY_price2031',
        'price2032': 'CY_price2032',
        'price2033': 'CY_price2033',
        'price2034': 'CY_price2034',
        'price2035': 'CY_price2035',
        'price2036': 'CY_price2036',
        'price2037': 'CY_price2037',
        'price2038': 'CY_price2038',
        'price2039': 'CY_price2039',
        'price2040': 'CY_price2040',
        'price2041': 'CY_price2041',
        'price2042': 'CY_price2042',
        'price2043': 'CY_price2043',
        'price2044': 'CY_price2044',

        'vhk2020': 'CY_vhk2020',
        'vhk2021': 'CY_vhk2021',
        'vhk2022': 'CY_vhk2022',
        'vhk2023': 'CY_vhk2023',
        'vhk2024': 'CY_vhk2024',
        'vhk2025': 'CY_vhk2025',
        'vhk2026': 'CY_vhk2026',
        'vhk2027': 'CY_vhk2027',
        'vhk2028': 'CY_vhk2028',
        'vhk2029': 'CY_vhk2029',
        'vhk2030': 'CY_vhk2030',
        'vhk2031': 'CY_vhk2031',
        'vhk2032': 'CY_vhk2032',
        'vhk2033': 'CY_vhk2033',
        'vhk2034': 'CY_vhk2034',
        'vhk2035': 'CY_vhk2035',
        'vhk2036': 'CY_vhk2036',
        'vhk2037': 'CY_vhk2037',
        'vhk2038': 'CY_vhk2038',
        'vhk2039': 'CY_vhk2039',
        'vhk2040': 'CY_vhk2040',
        'vhk2041': 'CY_vhk2041',
        'vhk2042': 'CY_vhk2042',
        'vhk2043': 'CY_vhk2043',
        'vhk2044': 'CY_vhk2044',

        'gm2020': 'CY_gm2020',
        'gm2021': 'CY_gm2021',
        'gm2022': 'CY_gm2022',
        'gm2023': 'CY_gm2023',
        'gm2024': 'CY_gm2024',
        'gm2025': 'CY_gm2025',
        'gm2026': 'CY_gm2026',
        'gm2027': 'CY_gm2027',
        'gm2028': 'CY_gm2028',
        'gm2029': 'CY_gm2029',
        'gm2030': 'CY_gm2030',
        'gm2031': 'CY_gm2031',
        'gm2032': 'CY_gm2032',
        'gm2033': 'CY_gm2033',
        'gm2034': 'CY_gm2034',
        'gm2035': 'CY_gm2035',
        'gm2036': 'CY_gm2036',
        'gm2037': 'CY_gm2037',
        'gm2038': 'CY_gm2038',
        'gm2039': 'CY_gm2039',
        'gm2040': 'CY_gm2040',
        'gm2041': 'CY_gm2041',
        'gm2042': 'CY_gm2042',
        'gm2043': 'CY_gm2043',
        'gm2044': 'CY_gm2044',

        'wVol2020': 'CY_wVol2020',
        'wVol2021': 'CY_wVol2021',
        'wVol2022': 'CY_wVol2022',
        'wVol2023': 'CY_wVol2023',
        'wVol2024': 'CY_wVol2024',
        'wVol2025': 'CY_wVol2025',
        'wVol2026': 'CY_wVol2026',
        'wVol2027': 'CY_wVol2027',
        'wVol2028': 'CY_wVol2028',
        'wVol2029': 'CY_wVol2029',
        'wVol2030': 'CY_wVol2030',
        'wVol2031': 'CY_wVol2031',
        'wVol2032': 'CY_wVol2032',
        'wVol2033': 'CY_wVol2033',
        'wVol2034': 'CY_wVol2034',
        'wVol2035': 'CY_wVol2035',
        'wVol2036': 'CY_wVol2036',
        'wVol2037': 'CY_wVol2037',
        'wVol2038': 'CY_wVol2038',
        'wVol2039': 'CY_wVol2039',
        'wVol2040': 'CY_wVol2040',
        'wVol2041': 'CY_wVol2041',
        'wVol2042': 'CY_wVol2042',
        'wVol2043': 'CY_wVol2043',
        'wVol2044': 'CY_wVol2044',

        'wRev2020': 'CY_wRev2020',
        'wRev2021': 'CY_wRev2021',
        'wRev2022': 'CY_wRev2022',
        'wRev2023': 'CY_wRev2023',
        'wRev2024': 'CY_wRev2024',
        'wRev2025': 'CY_wRev2025',
        'wRev2026': 'CY_wRev2026',
        'wRev2027': 'CY_wRev2027',
        'wRev2028': 'CY_wRev2028',
        'wRev2029': 'CY_wRev2029',
        'wRev2030': 'CY_wRev2030',
        'wRev2031': 'CY_wRev2031',
        'wRev2032': 'CY_wRev2032',
        'wRev2033': 'CY_wRev2033',
        'wRev2034': 'CY_wRev2034',
        'wRev2035': 'CY_wRev2035',
        'wRev2036': 'CY_wRev2036',
        'wRev2037': 'CY_wRev2037',
        'wRev2038': 'CY_wRev2038',
        'wRev2039': 'CY_wRev2039',
        'wRev2040': 'CY_wRev2040',
        'wRev2041': 'CY_wRev2041',
        'wRev2042': 'CY_wRev2042',
        'wRev2043': 'CY_wRev2043',
        'wRev2044': 'CY_wRev2044'
    })

    return boupCY


def BoUpFy(dfAllBoUp):
    adj_boup = dfAllBoUp.drop(['vol2020', 'vol2021', 'vol2022', 'vol2023', 'vol2024', 'vol2025', 'vol2026', 'vol2027', 'vol2028', 'vol2029', 'vol2030', 'vol2031', 'vol2032', 'vol2033', 'vol2034', 'vol2035', 'vol2036', 'vol2037', 'vol2038', 'vol2039', 'vol2040', 'vol2041', 'vol2042', 'vol2043', 'vol2044',
                               'gm2020', 'gm2021', 'gm2022', 'gm2023', 'gm2024', 'gm2025', 'gm2026', 'gm2027', 'gm2028', 'gm2029', 'gm2030', 'gm2031', 'gm2032', 'gm2033', 'gm2034', 'gm2035', 'gm2036', 'gm2037', 'gm2038', 'gm2039', 'gm2040', 'gm2041', 'gm2042', 'gm2043', 'gm2044',
                               'wVol2020', 'wVol2021', 'wVol2022', 'wVol2023', 'wVol2024', 'wVol2025', 'wVol2026', 'wVol2027', 'wVol2028', 'wVol2029', 'wVol2030', 'wVol2031', 'wVol2032', 'wVol2033', 'wVol2034', 'wVol2035', 'wVol2036', 'wVol2037', 'wVol2038', 'wVol2039', 'wVol2040', 'wVol2041', 'wVol2042', 'wVol2043', 'wVol2044',
                               'wRev2020', 'wRev2021', 'wRev2022', 'wRev2023', 'wRev2024', 'wRev2025', 'wRev2026', 'wRev2027', 'wRev2028', 'wRev2029', 'wRev2030', 'wRev2031', 'wRev2032', 'wRev2033', 'wRev2034', 'wRev2035', 'wRev2036', 'wRev2037', 'wRev2038', 'wRev2039', 'wRev2040', 'wRev2041', 'wRev2042', 'wRev2043', 'wRev2044'], axis=1)
    boupFY = adj_boup.rename(columns={
        'fy_vol2020': 'FY_vol2020',
        'fy_vol2021': 'FY_vol2021',
        'fy_vol2022': 'FY_vol2022',
        'fy_vol2023': 'FY_vol2023',
        'fy_vol2024': 'FY_vol2024',
        'fy_vol2025': 'FY_vol2025',
        'fy_vol2026': 'FY_vol2026',
        'fy_vol2027': 'FY_vol2027',
        'fy_vol2028': 'FY_vol2028',
        'fy_vol2029': 'FY_vol2029',
        'fy_vol2030': 'FY_vol2030',
        'fy_vol2031': 'FY_vol2031',
        'fy_vol2032': 'FY_vol2032',
        'fy_vol2033': 'FY_vol2033',
        'fy_vol2034': 'FY_vol2034',
        'fy_vol2035': 'FY_vol2035',
        'fy_vol2036': 'FY_vol2036',
        'fy_vol2037': 'FY_vol2037',
        'fy_vol2038': 'FY_vol2038',
        'fy_vol2039': 'FY_vol2039',
        'fy_vol2040': 'FY_vol2040',
        'fy_vol2041': 'FY_vol2041',
        'fy_vol2042': 'FY_vol2042',
        'fy_vol2043': 'FY_vol2043',
        'fy_vol2044': 'FY_vol2044',

        'fy_volCustomer2020': 'FY_volCustomer2020',
        'fy_volCustomer2021': 'FY_volCustomer2021',
        'fy_volCustomer2022': 'FY_volCustomer2022',
        'fy_volCustomer2023': 'FY_volCustomer2023',
        'fy_volCustomer2024': 'FY_volCustomer2024',
        'fy_volCustomer2025': 'FY_volCustomer2025',
        'fy_volCustomer2026': 'FY_volCustomer2026',
        'fy_volCustomer2027': 'FY_volCustomer2027',
        'fy_volCustomer2028': 'FY_volCustomer2028',
        'fy_volCustomer2029': 'FY_volCustomer2029',
        'fy_volCustomer2030': 'FY_volCustomer2030',
        'fy_volCustomer2031': 'FY_volCustomer2031',
        'fy_volCustomer2032': 'FY_volCustomer2032',
        'fy_volCustomer2033': 'FY_volCustomer2033',
        'fy_volCustomer2034': 'FY_volCustomer2034',
        'fy_volCustomer2035': 'FY_volCustomer2035',
        'fy_volCustomer2036': 'FY_volCustomer2036',
        'fy_volCustomer2037': 'FY_volCustomer2037',
        'fy_volCustomer2038': 'FY_volCustomer2038',
        'fy_volCustomer2039': 'FY_volCustomer2039',
        'fy_volCustomer2040': 'FY_volCustomer2040',
        'fy_volCustomer2041': 'FY_volCustomer2041',
        'fy_volCustomer2042': 'FY_volCustomer2042',
        'fy_volCustomer2043': 'FY_volCustomer2043',
        'fy_volCustomer2044': 'FY_volCustomer2044',

        'fy_price2020': 'FY_price2020',
        'fy_price2021': 'FY_price2021',
        'fy_price2022': 'FY_price2022',
        'fy_price2023': 'FY_price2023',
        'fy_price2024': 'FY_price2024',
        'fy_price2025': 'FY_price2025',
        'fy_price2026': 'FY_price2026',
        'fy_price2027': 'FY_price2027',
        'fy_price2028': 'FY_price2028',
        'fy_price2029': 'FY_price2029',
        'fy_price2030': 'FY_price2030',
        'fy_price2031': 'FY_price2031',
        'fy_price2032': 'FY_price2032',
        'fy_price2033': 'FY_price2033',
        'fy_price2034': 'FY_price2034',
        'fy_price2035': 'FY_price2035',
        'fy_price2036': 'FY_price2036',
        'fy_price2037': 'FY_price2037',
        'fy_price2038': 'FY_price2038',
        'fy_price2039': 'FY_price2039',
        'fy_price2040': 'FY_price2040',
        'fy_price2041': 'FY_price2041',
        'fy_price2042': 'FY_price2042',
        'fy_price2043': 'FY_price2043',
        'fy_price2044': 'FY_price2044',

        'fy_vhk2020': 'FY_vhk2020',
        'fy_vhk2021': 'FY_vhk2021',
        'fy_vhk2022': 'FY_vhk2022',
        'fy_vhk2023': 'FY_vhk2023',
        'fy_vhk2024': 'FY_vhk2024',
        'fy_vhk2025': 'FY_vhk2025',
        'fy_vhk2026': 'FY_vhk2026',
        'fy_vhk2027': 'FY_vhk2027',
        'fy_vhk2028': 'FY_vhk2028',
        'fy_vhk2029': 'FY_vhk2029',
        'fy_vhk2030': 'FY_vhk2030',
        'fy_vhk2031': 'FY_vhk2031',
        'fy_vhk2032': 'FY_vhk2032',
        'fy_vhk2033': 'FY_vhk2033',
        'fy_vhk2034': 'FY_vhk2034',
        'fy_vhk2035': 'FY_vhk2035',
        'fy_vhk2036': 'FY_vhk2036',
        'fy_vhk2037': 'FY_vhk2037',
        'fy_vhk2038': 'FY_vhk2038',
        'fy_vhk2039': 'FY_vhk2039',
        'fy_vhk2040': 'FY_vhk2040',
        'fy_vhk2041': 'FY_vhk2041',
        'fy_vhk2042': 'FY_vhk2042',
        'fy_vhk2043': 'FY_vhk2043',
        'fy_vhk2044': 'FY_vhk2044',

        'fy_gm2020': 'FY_gm2020',
        'fy_gm2021': 'FY_gm2021',
        'fy_gm2022': 'FY_gm2022',
        'fy_gm2023': 'FY_gm2023',
        'fy_gm2024': 'FY_gm2024',
        'fy_gm2025': 'FY_gm2025',
        'fy_gm2026': 'FY_gm2026',
        'fy_gm2027': 'FY_gm2027',
        'fy_gm2028': 'FY_gm2028',
        'fy_gm2029': 'FY_gm2029',
        'fy_gm2030': 'FY_gm2030',
        'fy_gm2031': 'FY_gm2031',
        'fy_gm2032': 'FY_gm2032',
        'fy_gm2033': 'FY_gm2033',
        'fy_gm2034': 'FY_gm2034',
        'fy_gm2035': 'FY_gm2035',
        'fy_gm2036': 'FY_gm2036',
        'fy_gm2037': 'FY_gm2037',
        'fy_gm2038': 'FY_gm2038',
        'fy_gm2039': 'FY_gm2039',
        'fy_gm2040': 'FY_gm2040',
        'fy_gm2041': 'FY_gm2041',
        'fy_gm2042': 'FY_gm2042',
        'fy_gm2043': 'FY_gm2043',
        'fy_gm2044': 'FY_gm2044',

        'fy_wVol2020': 'FY_wVol2020',
        'fy_wVol2021': 'FY_wVol2021',
        'fy_wVol2022': 'FY_wVol2022',
        'fy_wVol2023': 'FY_wVol2023',
        'fy_wVol2024': 'FY_wVol2024',
        'fy_wVol2025': 'FY_wVol2025',
        'fy_wVol2026': 'FY_wVol2026',
        'fy_wVol2027': 'FY_wVol2027',
        'fy_wVol2028': 'FY_wVol2028',
        'fy_wVol2029': 'FY_wVol2029',
        'fy_wVol2030': 'FY_wVol2030',
        'fy_wVol2031': 'FY_wVol2031',
        'fy_wVol2032': 'FY_wVol2032',
        'fy_wVol2033': 'FY_wVol2033',
        'fy_wVol2034': 'FY_wVol2034',
        'fy_wVol2035': 'FY_wVol2035',
        'fy_wVol2036': 'FY_wVol2036',
        'fy_wVol2037': 'FY_wVol2037',
        'fy_wVol2038': 'FY_wVol2038',
        'fy_wVol2039': 'FY_wVol2039',
        'fy_wVol2040': 'FY_wVol2040',
        'fy_wVol2041': 'FY_wVol2041',
        'fy_wVol2042': 'FY_wVol2042',
        'fy_wVol2043': 'FY_wVol2043',
        'fy_wVol2044': 'FY_wVol2044',

        'fy_wRev2020': 'FY_wRev2020',
        'fy_wRev2021': 'FY_wRev2021',
        'fy_wRev2022': 'FY_wRev2022',
        'fy_wRev2023': 'FY_wRev2023',
        'fy_wRev2024': 'FY_wRev2024',
        'fy_wRev2025': 'FY_wRev2025',
        'fy_wRev2026': 'FY_wRev2026',
        'fy_wRev2027': 'FY_wRev2027',
        'fy_wRev2028': 'FY_wRev2028',
        'fy_wRev2029': 'FY_wRev2029',
        'fy_wRev2030': 'FY_wRev2030',
        'fy_wRev2031': 'FY_wRev2031',
        'fy_wRev2032': 'FY_wRev2032',
        'fy_wRev2033': 'FY_wRev2033',
        'fy_wRev2034': 'FY_wRev2034',
        'fy_wRev2035': 'FY_wRev2035',
        'fy_wRev2036': 'FY_wRev2036',
        'fy_wRev2037': 'FY_wRev2037',
        'fy_wRev2038': 'FY_wRev2038',
        'fy_wRev2039': 'FY_wRev2039',
        'fy_wRev2040': 'FY_wRev2040',
        'fy_wRev2041': 'FY_wRev2041',
        'fy_wRev2042': 'FY_wRev2042',
        'fy_wRev2043': 'FY_wRev2043',
        'fy_wRev2044': 'FY_wRev2044'
    })

    return boupFY