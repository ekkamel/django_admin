from django.contrib import admin
from .models import Category, Hero, Origin, Villain
import csv
from django.http import HttpResponse

admin.site.register(Category)
admin.site.register(Villain)

@admin.register(Hero)
# in this code block we filter the value of benevolence_factor to display 
# True if > 75 and False otherwise
class HeroAdmin(admin.ModelAdmin): 
    list_display = ("name", "is_immortal", "category", "origin", "is_very_benevolent")
    list_filter = ("is_immortal", "category", "origin", )

    
    # This is another method to create a calculated field in a model
    # The other method is in models.py 
    
    def is_very_benevolent(self, obj):
        return obj.benevolence_factor > 75
    
    # This line causes the field to look with a button and not True/False
    is_very_benevolent.boolean = True
    

    # You can add an action to the model admin !!
    actions = ["mark_immortal", "export_as_csv"]

    def mark_immortal(self, request, queryset): 
        queryset.update(is_immortal=True)
    
    
#actions = ["export_as_csv"]

    # how to export selected records to csv
    
    # This code has nothing specific about to Hero, therefore it can be encapsulated in 
    # a mixin and make it available to all entities
    ## class ExportCsvMixin: 
    # and then make available to each entity like this: 
    ## class HeroAdmin(admin.ModelAdmin, ExportCsvMixin):
    ## list_display = ...........
    ## list_filter = ............
    ## actions = ["export_as_csv"] 
     
    def export_as_csv(self, request, queryset): 
        
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)
        
        writer.writerow(field_names)
        for obj in queryset: 
            row = writer.writerow([getattr(obj, field) for field in field_names])
        
        return response
         

    export_as_csv.short_description = "Export Selected"

# In case you need to remove the Delete Selected from the menu of a model 

    def get_actions(self, request): 
        actions = super().get_actions(request)
        if 'delete_selected' in actions: 
            del actions['delete_selected']
        return actions


    
# to add a calculated field to the admin site side Filter bar you need
# to subclass the SimpleListFilter 

# aperantly this is missing something and I could not add the field to list_filter
class IsVeryBenevolentFilter(admin.SimpleListFilter): 
    title = 'is_very_benevolent'
    parameter_name = 'is_very_benevolent'
    
    def lookups(self, request, model_admin): 
        return (
            ('Yes', 'Yes'), 
            ('No', 'No')
        )
        
    def queryset(self, request, queryset):
        value = self.value()
        if value == 'Yes': 
            return queryset.filter(benevolence_factor__gt=75)
        elif value == 'No': 
            return queryset.exclude(benevolence_factor__gt=75)
        return queryset



@admin.register(Origin)
class OriginAdmin(admin.ModelAdmin):
    list_display = ("name", Origin.hero_count, Origin.villain_count )

# This is how to use order by for a calculated field    
Origin.hero_count.admin_order_field = '_hero_count'
Origin.villain_count.admin_order_field = '_villain_count'