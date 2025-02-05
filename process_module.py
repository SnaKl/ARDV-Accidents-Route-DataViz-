# pylint: disable=C0301, R0911, R0912, R0913, R0914, R0915

# disable pylint :
# line too long : C0301
# pylint problemes:
# fonction avec trop d'arguments (make_map, make_plot_map)
# résolutions possibles:
# revoir les fonctions, transformer les paramètres en dict
# class avec aucune méthode publique
# résolutions possibles:
# - transformer la classe en dataclass
# - supprimer totalement la classe et revoir la structure
"""
    Module pour aider à la création du dashboard
    permet une exécution rapide dans le dashboard
    en réduisant au maximum les processus lors de l'utilisation
"""
import statistics
import math
from functools import reduce
from shapely.geometry import Polygon
import geopandas as gpd
import pandas as pd
import plotly.express as px

import dash_core_components as dcc
import dash_html_components as html

#  labels dctionary
dict_labels = {
    "lum": {
        1: "Plein jour",
        2: "Crépuscule ou aube",
        3: "Nuit sans éclairage public",
        4: "Nuit avec éclairage public non allumé",
        5: "Nuit avec éclairage public allumé",
    },
    "atm": {
        -1: "Non renseigné",
        1: "Normale",
        2: "Pluie légère",
        3: "Pluie forte",
        4: "Neige - grêle",
        5: "Brouillard - fumée",
        6: "Vent fort - tempête",
        7: "Temps éblouissant",
        8: "Temps couvert",
        9: "Autre",
    },
    "col": {
        -1: "Non renseigné",
        1: "Deux véhicules - frontale",
        2: "Deux véhicules - par l’arrière",
        3: "Deux véhicules – par le coté",
        4: "Trois véhicules et plus – en chaîne",
        5: "Trois véhicules et plus - collisions multiples",
        6: "Autre collision",
        7: "Sans collision",
    },
    "catr": {
        1: "Autoroute",
        2: "Route nationale",
        3: "Route Départementale",
        4: "Voie Communales",
        5: "Hors réseau public",
        6: "Parc de stationnement ouvert à la circulation publique",
        7: "Routes de métropole urbaine",
        9: "autre",
    },
    "circ": {
        -1: "Non renseign",
        1: "A sens unique",
        2: "Bidirectionnelle",
        3: "A chaussées séparées",
        4: "Avec voies d’affectation variable",
    },
    "vosp": {
        -1: "Non renseigné",
        0: "Sans objet ",
        1: "Piste cyclable ",
        2: "Bande cyclable ",
        3: "Voie réservée",
    },
    "prof": {
        -1: "Non renseigné",
        1: "Plat ",
        2: "Pente",
        3: "Sommet de côte",
        4: "Bas de côte",
    },
    "plan": {
        -1: "Non renseigné ",
        1: "Partie rectiligne ",
        2: "En courbe à gauche ",
        3: "En courbe à droite",
        4: "En « S »",
    },
    "surf": {
        -1: "Non renseigné",
        1: "Normale",
        2: "Mouillée",
        3: "Flaques",
        4: "Inondée",
        5: "Enneigée",
        6: "Boue ",
        7: "Verglacée",
        8: "Corps gras – huile",
        9: "Autre",
    },
    "grav": {1: "Indemne", 2: "Tué", 3: "Blessé hospitalisé", 4: "Blessé léger"},
    "sexe": {1: "Masculin", 2: "Féminin"},
    "trajet": {
        -1: "Non renseigné",
        0: "Non renseigné",
        1: "Domicile – travail",
        2: "Domicile – école ",
        3: "Courses – achats ",
        4: "Utilisation professionnelle ",
        5: "Promenade – loisirs ",
        9: "Autre",
    },
    "choc": {
        -1: "Non renseigné",
        0: "Aucun",
        1: "Avant",
        2: "Avant droit",
        3: "Avant gauche",
        4: "Arrière",
        5: "Arrière droit",
        6: "Arrière gauche",
        7: "Côté droit",
        8: "Côté gauche",
        9: "Chocs multiples (tonneaux)",
    },
    "secu1": {
        -1: "Non renseigné",
        0: "Aucun équipement ",
        1: "Ceinture ",
        2: "Casque  ",
        3: "Dispositif enfants ",
        4: "Gilet réfléchissant",
        5: "Airbag (2RM/3RM)",
        6: "Gants (2RM/3RM)",
        7: "Gants + Airbag (2RM/3RM)",
        8: "Non déterminable ",
        9: "Autre",
    },
}

observable_values_labels = {
    "Jour": "jour",
    "Mois": "mois",
    "Heures": "rounded",
    "Luminosité": "lum",
    "Condition Atmosphérique": "atm",
    "Type de collision": "col",
    "Catégorie de route": "catr",
    "Régime de circulation": "circ",
    "Nombre total de voies de circulation": "nbv",
    "Existence d’une voie réservée": "vosp",
    "Déclivité de la route": "prof",
    "Tracé en plan": "plan",
    "Etat de la surface": "surf",
    "Vitesse maximale autorisée": "vma",
    "Gravité de blessure": "grav",
    "Sexe de l'usager": "sexe",
    "Année de naissance de l'usager": "an_nais",
    "Motif du déplacement": "trajet",
    "Point de choc initial": "choc",
    "Système de sécurité": "secu1",
}


def get_all_coords(geo_data):
    """
    Retourne toutes les coordonées possibles des polygones

    Parameters:
        geo_data: polygones

    Returns:
        [coordonnées de tous les polygones]
    """
    coords = []
    for geometry in geo_data["geometry"]:
        if isinstance(geometry) != Polygon:
            for multi_polygon in geometry:
                coords.append(multi_polygon.exterior.coords.xy)
        else:
            coords.append(geometry.exterior.coords.xy)
    return coords


def get_bounds(geo_data):
    """
    retourne les bornes de chaque geometry

    Parameters:
        geo_data: geo_data

    Returns:
        [bornes]
    """
    return geo_data["geometry"].bounds


def get_area(geo_data):
    """
    retourne l'aire de chaque geometry

    Parameters:
        geo_data: geo_data

    Returns:
        [area]
    """
    return geo_data["geometry"].area


def get_zoom(geo_data):
    """
    retourne le zoom de la map grâce à l'aire totale de la géométrie à visualiser

    Parameters:
        geo_data: geo_data

    Returns:
        [bornes]
    """
    area_sum = sum(get_area(geo_data))
    zoom = -math.sqrt(area_sum) * 2.1 + 9
    return zoom


def get_center_coords(antipodes):
    """
    retourne le centre des antipodes

    Parameters:
        antipodes: antipodes

    Returns:
        [longitude, latitude]
    """
    lat = antipodes["minx"] + (antipodes["maxx"] - antipodes["minx"]) / 2
    lon = antipodes["miny"] + (antipodes["maxy"] - antipodes["miny"]) / 2
    return [lon, lat]


def get_antipodes(geo_data):
    """
    retourne les antipodes

    Parameters:
        geo_data: geo_data

    Returns:
        {"minx": minx, "maxx": maxx, "miny": miny, "maxy": maxy}
    """
    bounds = get_bounds(geo_data)
    minx = statistics.mean(bounds["minx"])
    maxx = statistics.mean(bounds["maxx"])
    miny = statistics.mean(bounds["miny"])
    maxy = statistics.mean(bounds["maxy"])
    return {"minx": minx, "maxx": maxx, "miny": miny, "maxy": maxy}


def make_map(
    datas,
    geo_datas,
    feature_id_key,
    location,
    hover_name,
    hover_data,
    data_color,
    zoom_choice,
    coords,
    opacity_choice,
    label,
):
    """
    retourne la map color en fonction des paramètres (choropleth_mapbox)

    Parameters:
        datas: données à observer
        geo_data: geo_data
        feature_id_key: keys match entre geo_datas et datas (properties.'location')
        location: keys datas
        hover_name: nom au survol
        hover_data: [données à afficher au survol]
        data_color: données utilisées pour la couleur
        zoom_choice: zoom map
        coords: coordonnées de la map
        opacity_choice: opacité sur la map
        label: label à afficher = {"data_id": "label"},

    Returns:
        choropleth_mapbox
    """
    return px.choropleth_mapbox(
        datas,
        geojson=geo_datas,
        featureidkey=feature_id_key,
        locations=location,
        custom_data=["type"],
        hover_name=datas[hover_name],
        hover_data=[datas[string] for string in hover_data if 1],
        color=data_color,
        color_continuous_scale="Viridis",
        range_color=(min(datas[data_color]), max(datas[data_color])),
        mapbox_style="carto-positron",
        zoom=zoom_choice,
        center={"lat": coords[0], "lon": coords[1]},
        opacity=opacity_choice,
        labels=label,
    )


def make_plot_map(datas, zoom_choice):
    """
    retourne la map scatter des accidents de la route

    Parameters
    ----------
        datas : donnée avec Num_Acc, latitude, longitude
        zoom_choice : zoom map

    Returns
    ----------
    choropleth_mapbox
    """
    return px.scatter_mapbox(
        datas,
        lat=datas.lat,
        lon=datas.long,
        custom_data=["type"],
        hover_name=datas["Num_Acc"],
        hover_data={"lat": False, "long": False},
        zoom=zoom_choice,
    )


def make_adaptatif_histo(
    id_histo_graph,
    histo_value_param_dropdown,
    histo_color_param_dropdown,
    histo_histnorm_param_radio_btn,
    histo_barmode_param_radio_btn,
    default_figure=None,
):
    """
    retourne dash div contenent tout le nécessaire pour un histogramme avec des dropdown et radio button à l'id et options personnalisées

    Parameters
    ----------
        id_histo_graph : id de l'histogramme
        histo_value_param_dropdown : {'id': 'nom', 'options':[{'label':label, 'value':'value},], 'value':value}
        histo_color_param_dropdown : {'id': 'nom', 'options':[{'label':label, 'value':'value},], 'value':value}
        histo_histnorm_param_radio_btn : {'id': 'nom', 'options':[{'label':label, 'value':'value},], 'value':value}
        histo_barmode_param_radio_btn : {'id': 'nom', 'options':[{'label':label, 'value':'value},], 'value':value}
        default_figure = None permet d'initialiser l'histogramme avec une figure plotly

    Returns
    ----------
        dash div
    """
    if not default_figure:
        default_figure = {}
    return html.Div(
        [
            dcc.Graph(id=id_histo_graph, figure=default_figure),
            html.Div(
                [
                    # dropdown choix des valeurs
                    html.Div(
                        [
                            html.Label(
                                "Valeurs à observer",
                                htmlFor=histo_value_param_dropdown["id"],
                                style={"fontWeight": "bold"},
                            ),
                            dcc.Dropdown(
                                id=histo_value_param_dropdown["id"],
                                options=histo_value_param_dropdown["options"],
                                value=histo_value_param_dropdown["value"],
                                style={"width": 250, "textAlign": "left"},
                            ),
                        ],
                        style={"textAlign": "center"},
                    ),
                    # dropdown choix comparaison
                    html.Div(
                        [
                            html.Label(
                                "Comparateur", htmlFor=histo_color_param_dropdown["id"], style={"fontWeight": "bold"}
                            ),
                            dcc.Dropdown(
                                id=histo_color_param_dropdown["id"],
                                options=histo_color_param_dropdown["options"],
                                value=histo_color_param_dropdown["value"],
                                style={"width": 250, "textAlign": "left"},
                            ),
                        ],
                        style={"display": "block", "marginLeft": 10, "textAlign": "center"},
                    ),
                    # radio button paramètre d'affichage
                    html.Div(
                        [
                            html.Label(
                                "Paramètre d'affichage",
                                htmlFor=histo_histnorm_param_radio_btn["id"],
                                style={"fontWeight": "bold"},
                            ),
                            dcc.RadioItems(
                                id=histo_histnorm_param_radio_btn["id"],
                                options=histo_histnorm_param_radio_btn["options"],
                                value=histo_histnorm_param_radio_btn["value"],
                                style={"textAlign": "left", "margin": "auto"},
                            ),
                        ],
                        style={"display": "flex", "flexDirection": "column", "marginLeft": 10, "textAlign": "center"},
                    ),
                    # radio button paramètre d'affichage multiple
                    html.Div(
                        [
                            html.Label(
                                "Paramètre comparateur",
                                htmlFor=histo_barmode_param_radio_btn["id"],
                                style={"fontWeight": "bold"},
                            ),
                            dcc.RadioItems(
                                id=histo_barmode_param_radio_btn["id"],
                                options=histo_barmode_param_radio_btn["options"],
                                value=histo_barmode_param_radio_btn["value"],
                                style={"textAlign": "left", "margin": "auto"},
                            ),
                        ],
                        style={"display": "flex", "flexDirection": "column", "marginLeft": 10, "textAlign": "center"},
                    ),
                ],
                style={"display": "flex", "justifyContent": "center"},
            ),
        ]
    )


def update_histo(values_param, color_param, histnorm_param, barmode_param, datas):
    """
    retourne l'histogramme en fonction des paramètres fournie

    Parameters
    ----------
        values_param : valeur à observer (nom collonne)
        color_param : valeur de comparaison (nom collonne)
        histnorm_param : paramètre histonorm
        barmode_param : paramètre barmode
        datas : dataframe

    Returns
    ----------
        fig histo
    """
    # si aucune valeur séléctionnée
    if not values_param:
        return None

    bargap_param = 0
    # si valeur et comparaison sont pareilles
    if values_param == color_param:
        return None

    # si pas de choix (none)
    if not histnorm_param:
        histnorm_param = ""

    # valeurs choisies par l'utilisateur
    loc = [values_param]
    if color_param:
        loc += [color_param]

    # récupère seulement les valeurs choisies dans all_merged
    dataframe = datas.loc[:, loc]
    # si pas de colorParem
    if not color_param:
        fig = px.histogram(dataframe, x=values_param, histnorm=histnorm_param)
    else:
        fig = px.histogram(dataframe, x=values_param, color=color_param, histnorm=histnorm_param, barmode=barmode_param)

    # affichage des pourcentages
    if histnorm_param == "percent":
        fig.update_yaxes(ticksuffix="%")

    # si groupe espace les valeurs
    if barmode_param == "group" and color_param:
        bargap_param = 0.2

    fig.update_layout(
        xaxis_title=values_param,
        yaxis_title="Accidents",
        legend_title=color_param,
        bargap=bargap_param,
    )

    return fig


class ClassMap:
    """
    class qui représente toutes les info des accident et de leurs cartes liées\n
    class actuellement peu utile mais vise à être développée pour permettre une plus grande modularisation du code

    Attributes
    ----------
    geojson = {"departments","communes"}
        données brut des geojson\n
    csv : {"characteristics", "places", "users", "vehicle"}
        données brut des accidents\n
    all_merged : dataframe
        toutes les données accident merge\n
    accident_dep : nombre d'accident par département\n
    accident_com : nombre d'accident par commune\n
    departments_info : info liée à chaque département (tiré de departement geojson)\n
    communes_info : info lié à chaque commune (tiré de commune geojson)\n
    default_map = departments_map : map département part défaut (carte color nombre d'accident par département)\n
    communes_map :  map commune défaut (carte color nombre d'accident par commune)\n
    departments_map_info : informations liées à la carte\n
    communes_map_info : informations liées à la carte\n

    Methods
    -------
        actuellement  que des méthodes privées
    """

    __raw_departements = gpd.read_file("./geojson/departements.geojson")
    __raw_communes = gpd.read_file("./geojson/communes.geojson")
    geojson = {
        "departments": __raw_departements,
        "communes": __raw_communes,
    }
    # données brut
    __raw_caracteristiques = pd.read_csv("./csv/accident/caracteristiques-2019.csv", sep=";", decimal=",")
    __raw_lieux = pd.read_csv("./csv/accident/lieux-2019.csv", sep=";", decimal=",")
    __raw_usagers = pd.read_csv("./csv/accident/usagers-2019.csv", sep=";", decimal=",")
    __raw_vehicules = pd.read_csv("./csv/accident/vehicules-2019.csv", sep=";", decimal=",")
    csv = {
        "characteristics": __raw_caracteristiques,
        "places": __raw_lieux,
        "users": __raw_usagers,
        "vehicle": __raw_vehicules,
    }

    def __init__(self):
        # arondi à l'heure près. ex: 02:54 -> 2
        self.csv["characteristics"] = self.__rounded_hour_caracteristique()
        # merged toutes les informations brut grâce au Num_Acc
        self.all_merged = reduce(
            lambda left, right: pd.merge(left, right, on=["Num_Acc"], how="outer"),
            [
                self.__raw_caracteristiques,
                self.__raw_lieux,
                self.__raw_usagers,
                self.__raw_vehicules,
            ],
        )
        # remplace toute les valeurs par colonne dans le dict_labels
        self.__replace_labels_merged()
        # token nécessaire pour la map
        px.set_mapbox_access_token(
            "pk.eyJ1Ijoic25ha2wiLCJhIjoiY2tpeXhqYmQzMWl0NTJ6bno4dzV4amJnayJ9.-qT1chzjLoOM6N1RDv_Zag"
        )
        # récupère les informations des départements et rename
        self.departments_info = self.__raw_departements.loc[
            :, ~self.__raw_departements.columns.isin(["id", "geometry"])
        ].rename(columns={"nom_dep0": "nom_dep_maj", "region0": "region"})
        # nombre d'accident par departement
        self.accident_dep = self.__get_accident_dep()
        # info par communes
        self.communes_info = self.__raw_communes.loc[:, ~self.__raw_communes.columns.isin(["geometry"])]
        # nombre d'accident par commune
        self.accident_com = self.__get_accident_com()
        # crée la map par défault qui est la map département (toute)
        self.default_map = self.departments_map = make_map(
            self.accident_dep,
            self.geojson["departments"],
            "properties.insee_dep",
            "insee_dep",
            "nom_dep",
            ["insee_dep", "nb_accident"],
            "nb_accident",
            1.2,
            [16.8669662, 7.0432566],
            1,
            {"insee_dep": "Département", "nb_accident": "Nombre d'accidents"},
        )
        # information sur la map département
        self.departments_map_info = {
            "hoverText": self.departments_map["data"][0]["hovertext"],
            "locations": self.departments_map["data"][0]["locations"],
            "size": len(self.departments_map["data"][0]["hovertext"]),
            "mergeText": sorted(
                [
                    f"{self.departments_map['data'][0]['locations'][i]} {self.departments_map['data'][0]['hovertext'][i]}"
                    for i in range(len(self.departments_map["data"][0]["hovertext"]))
                ]
            ),
        }
        # crée la map commune (toute)
        self.communes_map = make_map(
            self.accident_com,
            self.geojson["communes"],
            "properties.insee_com",
            "insee_com",
            "nom_comm",
            ["postal_code", "nb_accident"],
            "nb_accident",
            1.2,
            [16.8669662, 7.0432566],
            1,
            {
                "insee_com": "Code INSEE",
                "postal_code": "Code postal",
                "nb_accident": "Nombre d'accidents",
            },
        )
        # information sur la map commune
        self.communes_map_info = {
            "hoverText": self.communes_map["data"][0]["hovertext"],
            "locations": self.communes_map["data"][0]["locations"],
            "size": len(self.communes_map["data"][0]["hovertext"]),
            "mergeText": sorted(
                [
                    f"{self.communes_map['data'][0]['locations'][i]} {self.communes_map['data'][0]['hovertext'][i]}"
                    for i in range(len(self.communes_map["data"][0]["hovertext"]))
                ]
            ),
        }

    def __rounded_hour_caracteristique(self):
        """crée une colonne rounded avec les valuers arondis à l'heure près pour chaque accident. ex: 02:54 -> 2"""
        temp = self.csv["characteristics"]
        # crée la colonne rounded
        temp["rounded"] = ""
        # pour chaque heure
        for roudend_hour in range(24):
            # pour chaque row
            for ind in temp.index:
                # récupère l'heure (split(':') hh:mm)
                heures = temp["hrmn"][ind].split(":")[0]
                if int(heures) == roudend_hour:
                    temp.loc[[ind], "rounded"] = roudend_hour
        return temp

    def __replace_labels_merged(self):
        """remplace toutes les valeurs de chaque ligne pour chaque colonnes en fonction de dict_labels"""
        for label in dict_labels:
            item, data = [], []
            for key, value in dict_labels[label].items():
                item += [key]
                data += [value]
            self.all_merged.loc[:, label] = self.all_merged[label].replace(item, data)

    def __get_accident_dep(self):
        """
        retourne le nombre d'accident par département

        Returns: dataframe
        """
        nb_accident_dep = (
            self.__raw_caracteristiques.dep.astype(str)
            .str.zfill(2)
            .value_counts()
            .rename_axis("insee_dep")
            .reset_index(name="nb_accident")
        )
        merge = pd.merge(nb_accident_dep, self.departments_info, on="insee_dep")
        merge["type"] = ["department" for string in range(len(merge.index))]
        return merge

    def __get_accident_com(self):
        """
        retourne le nombre d'accident par commune

        Returns:
            dataframe
        """
        accident_communes = (
            self.__raw_caracteristiques.com.value_counts().rename_axis("insee_com").reset_index(name="nb_accident")
        )
        merge = pd.merge(accident_communes, self.communes_info, on="insee_com")
        merge["type"] = ["commune" for string in range(len(merge.index))]
        return merge
