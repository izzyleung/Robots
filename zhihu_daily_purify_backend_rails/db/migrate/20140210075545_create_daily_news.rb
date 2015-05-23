class CreateDailyNews < ActiveRecord::Migration
  def change
    create_table :daily_news do |t|
      t.string :date
      t.text :content

      t.timestamps
    end
  end
end
